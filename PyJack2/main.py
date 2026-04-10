import csv
import io
import base64
from nicegui import ui
from database import DatabaseManager
from domain import Game, Card, GameState

db_manager = DatabaseManager()


# ============================================================================
# HAUPTMENUE (/)
# ============================================================================
@ui.page('/')
def render_main_menu() -> None:
    ui.query('body').style('margin: 0; padding: 0; background-color: #0f172a;')
    with ui.column().classes('w-full min-h-screen items-center justify-center text-white p-0 m-0'):
        with ui.column().classes('items-center mb-12'):
            ui.label('🎰').classes('text-7xl mb-4')
            ui.label('PYJACK').classes('text-6xl font-bold text-yellow-500 tracking-widest drop-shadow-lg')
            ui.label('B L A C K J A C K').classes('text-yellow-500/50 tracking-[0.5em] text-sm mt-2')
            ui.label('FHNW Wirtschaftsinformatik | OOP SS26').classes('text-xs text-gray-400 mt-6 tracking-widest')

        with ui.column().classes('items-center gap-4 w-72'):
            ui.button('🃏 Spiel starten', on_click=lambda: ui.navigate.to('/game')) \
                .classes('w-full py-3').props('color=green-800 size=lg')
            ui.button('◈ Spielhistorie', on_click=lambda: ui.navigate.to('/history')) \
                .classes('w-full py-3').props('color=blue-900 size=lg')
            ui.button('◎ Einstellungen', on_click=lambda: ui.navigate.to('/settings')) \
                .classes('w-full py-3').props('color=slate-800 size=lg')


# ============================================================================
# SPIELTISCH (/game)
# ============================================================================
class GamePageUI:
    def __init__(self):
        self.settings = db_manager.get_settings()
        self.game = Game(db_manager)

        self.container_dealer_cards = None
        self.container_player_cards = None
        self.label_dealer_score = None
        self.label_player_score = None
        self.label_game_status = None
        self.btn_hit = None
        self.btn_stand = None
        self.btn_new = None
        self.dialog_game_over = None
        self.dialog_title = None
        self.dialog_message = None

    def render_card_obj(self, card: Card) -> None:
        text_color = 'red' if card.suit.color == 'red' else 'black'
        # Scale back visually to fix browser zoom layout issues and remove any margin/overflow with inline padding.
        # Add position relative to place bottom items absolutely inside the border.
        with ui.card().style(f'width: 70px; height: 100px; position: relative; padding: 4px; background-color: white; color: {text_color}; border: 1px solid gray; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'):
            # Top-Left Element
            with ui.column().style('position: absolute; top: 4px; left: 4px; align-items: center; gap: 0; line-height: 1;'):
                ui.label(card.rank.symbol).style('font-weight: bold; font-size: 14px; margin: 0; padding: 0;')
                ui.label(card.suit.symbol).style('font-size: 12px; margin: 0; padding: 0;')

            # Center Symbol
            center_sym = {'J': '♞', 'Q': '♛', 'K': '♚'}.get(card.rank.symbol, card.suit.symbol)
            with ui.row().style('position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);'):
                ui.label(center_sym).style('font-size: 28px; font-weight: normal;')

            # Bottom-Right Element (rotated)
            with ui.column().style('position: absolute; bottom: 4px; right: 4px; align-items: center; gap: 0; line-height: 1; transform: rotate(180deg);'):
                ui.label(card.rank.symbol).style('font-weight: bold; font-size: 14px; margin: 0; padding: 0;')
                ui.label(card.suit.symbol).style('font-size: 12px; margin: 0; padding: 0;')

    def render_hidden_card_obj(self) -> None:
        back_color = self.settings.get('card_back', '#1e3a8a')
        if back_color.startswith('bg-'):
            back_color = '#1e3a8a'
        ui.card().style(f'width: 70px; height: 100px; background-color: {back_color}; border: 2px solid rgba(255,255,255,0.2); border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);')

    def update_ui(self) -> None:
        if (
            self.container_dealer_cards is None
            or self.container_player_cards is None
            or self.label_dealer_score is None
            or self.label_player_score is None
            or self.label_game_status is None
            or self.btn_hit is None
            or self.btn_stand is None
            or self.btn_new is None
            or self.dialog_game_over is None
            or self.dialog_title is None
            or self.dialog_message is None
        ):
            return

        # --- Dealer-Karten ---
        self.container_dealer_cards.clear()
        with self.container_dealer_cards:
            if self.game.dealer.hand.cards:
                if self.game.dealer.hide_first_card and len(self.game.dealer.hand.cards) >= 2:
                    self.render_hidden_card_obj()
                    for c in self.game.dealer.hand.cards[1:]:
                        self.render_card_obj(c)
                else:
                    for c in self.game.dealer.hand.cards:
                        self.render_card_obj(c)

        # --- Spieler-Karten ---
        self.container_player_cards.clear()
        with self.container_player_cards:
            for c in self.game.player.hand.cards:
                self.render_card_obj(c)

        # --- Scores ---
        is_hidden = self.game.dealer.hide_first_card and self.game.state == GameState.PLAYER_TURN
        if is_hidden:
            self.label_dealer_score.text = f'Punkte: {self.game.dealer.get_visible_score()} + ?'
        else:
            self.label_dealer_score.text = f'Punkte: {self.game.dealer.get_score()}'

        player_pts = self.game.player.get_score()
        hint_text = ''
        if self.settings.get('show_hints', True) and self.game.state == GameState.PLAYER_TURN:
            if player_pts <= 16:
                hint_text = ' (Hit empfohlen)'
            elif player_pts >= 17:
                hint_text = ' (Stand empfohlen)'
        self.label_player_score.text = f'Punkte: {player_pts}{hint_text}'

        # --- Buttons ---
        is_active = self.game.can_player_act()
        self.btn_hit.set_enabled(is_active)
        self.btn_stand.set_enabled(is_active)
        self.btn_new.set_enabled(not is_active)

        # --- Status & Dialog ---
        if self.game.state == GameState.GAME_OVER:
            self.label_game_status.text = 'Runde beendet!'
            if self.game.winner == 'Spieler':
                self.dialog_title.text = 'GEWONNEN!'
                self.dialog_title.classes(replace='text-3xl font-bold text-green-500 mb-2')
                self.dialog_message.text = 'Glückwunsch!'
            elif self.game.winner == 'Dealer':
                self.dialog_title.text = 'VERLOREN'
                self.dialog_title.classes(replace='text-3xl font-bold text-red-500 mb-2')
                self.dialog_message.text = 'Der Dealer gewinnt.'
            else:
                self.dialog_title.text = 'PUSH'
                self.dialog_title.classes(replace='text-3xl font-bold text-yellow-500 mb-2')
                self.dialog_message.text = 'Unentschieden.'
            self.dialog_game_over.open()
        elif self.game.state == GameState.PLAYER_TURN:
            self.label_game_status.text = 'Dein Zug – Hit oder Stand?'
        else:
            self.label_game_status.text = 'Dealer zieht...'

    def handle_new_game(self) -> None:
        if self.dialog_game_over is not None:
            self.dialog_game_over.close()
        self.game.start_new_game()
        self.update_ui()

    def handle_hit(self) -> None:
        self.game.player_hit()
        if (
            self.settings.get('auto_stand_21', True)
            and self.game.player.get_score() == 21
            and self.game.state == GameState.PLAYER_TURN
        ):
            self.game.player_stand()
        self.update_ui()

    def handle_stand(self) -> None:
        self.game.player_stand()
        self.update_ui()

    def build_layout(self) -> None:
        bg_color = self.settings.get('table_color', '#163824')
        ui.query('body').style(f'margin: 0; padding: 0; background-color: {bg_color};')

        with ui.column().classes('w-full min-h-screen items-center text-white p-0 m-0').style(
            f'background-color: {bg_color};'
        ):
            # Navigationsleiste
            with ui.row().classes(
                'w-full max-w-4xl justify-between items-center py-2 px-4 mb-2 mt-4 '
                'bg-black/40 rounded-xl border border-white/10'
            ):
                ui.button('← Menü', on_click=lambda: ui.navigate.to('/')).props('flat color=yellow')
                ui.label('PyJack Tisch').classes('text-xl font-bold text-yellow-500')
                ui.label('OOP SS26').classes('text-xs text-gray-400')

            # Spielfeld
            with ui.card().classes(
                'w-full max-w-4xl bg-black/30 p-4 items-center '
                'border border-white/10 shadow-2xl rounded-2xl min-h-[400px]'
            ):
                # Dealer-Bereich
                with ui.column().classes('w-full items-center bg-black/40 p-2 rounded-xl mb-2 shadow-inner'):
                    ui.label('DEALER').classes('text-gray-400 text-xs tracking-widest font-bold')
                    self.label_dealer_score = ui.label('-').classes('text-yellow-400 font-bold mb-1 text-sm')
                    self.container_dealer_cards = ui.row().classes('gap-3 justify-center min-h-[105px] flex-wrap')

                self.label_game_status = ui.label('Klicke auf Neues Spiel').classes(
                    'text-xl font-bold text-white my-3 drop-shadow'
                )

                # Spieler-Bereich
                with ui.column().classes('w-full items-center bg-black/40 p-2 rounded-xl mt-2 shadow-inner'):
                    ui.label('SPIELER').classes('text-gray-400 text-xs tracking-widest font-bold')
                    self.label_player_score = ui.label('-').classes('text-green-400 font-bold mb-1 text-sm')
                    self.container_player_cards = ui.row().classes('gap-3 justify-center min-h-[105px] flex-wrap')

                # Aktions-Buttons
                with ui.row().classes('gap-4 mt-6'):
                    self.btn_new = ui.button('Neues Spiel', on_click=self.handle_new_game) \
                        .props('color=green-900 size=md').classes('px-6 py-2')
                    self.btn_hit = ui.button('Hit', on_click=self.handle_hit) \
                        .props('color=blue-900 size=md').classes('px-6 py-2')
                    self.btn_stand = ui.button('Stand', on_click=self.handle_stand) \
                        .props('color=orange-900 size=md').classes('px-6 py-2')

            # Game-Over-Dialog
            with ui.dialog() as self.dialog_game_over, ui.card().classes(
                'bg-slate-900 text-white items-center p-10 '
                'border border-white/20 rounded-2xl shadow-2xl'
            ):
                self.dialog_title = ui.label('').classes('text-3xl font-bold mb-2')
                self.dialog_message = ui.label('').classes('text-lg text-gray-300 mb-8')
                ui.button('Nochmal spielen', on_click=self.handle_new_game).props('color=green-700 size=lg').classes('w-full')
                ui.button('Zurück zum Menü', on_click=lambda: ui.navigate.to('/')).props('flat color=gray-400').classes('w-full mt-2')

@ui.page('/game')
def render_game() -> None:
    page = GamePageUI()
    page.build_layout()

# ============================================================================
# SPIELHISTORIE (/history)
# ============================================================================
@ui.page('/history')
def render_history() -> None:
    ui.query('body').style('margin: 0; padding: 0; background-color: #0f172a;')
    with ui.column().classes('w-full min-h-screen items-center p-6 text-white'):
        with ui.row().classes('w-full max-w-4xl justify-between items-center mb-6 bg-black/40 p-4 rounded-xl'):
            ui.button('← Menü', on_click=lambda: ui.navigate.to('/')).props('flat color=yellow')
            ui.label('Spielhistorie').classes('text-2xl font-bold text-yellow-500 drop-shadow')
            ui.button('Löschen', on_click=lambda: (db_manager.delete_all_games(), ui.navigate.reload())).props('outline color=red')
            
        stats = db_manager.get_statistics()
        
        with ui.row().classes('w-full max-w-4xl gap-6 mb-8 items-stretch'):
            # Statistik Details
            with ui.card().classes('flex-1 bg-black/30 p-6 border border-white/10 rounded-2xl items-center justify-center'):
                ui.label(f"Gesamtspiele: {stats['total_games']}").classes('text-xl font-bold mb-2')
                ui.label(f"👑 Spieler-Siege: {stats['player_wins']}").classes('text-green-400 text-lg')
                ui.label(f"💀 Dealer-Siege: {stats['dealer_wins']}").classes('text-red-400 text-lg')
                ui.label(f"👔 Unentschieden: {stats['draws']}").classes('text-yellow-400 text-lg')
                ui.label(f"📈 Win-Rate: {stats['player_win_rate']:.1f}%").classes('text-blue-400 text-xl font-bold mt-4')

            # Echarts Diagramm
            with ui.card().classes('flex-1 bg-black/30 p-4 border border-white/10 rounded-2xl h-64'):
                if stats['total_games'] > 0:
                    ui.echart({
                        'tooltip': {'trigger': 'item'},
                        'legend': {'bottom': '0%', 'textStyle': {'color': '#ffffff'}},
                        'series': [{
                            'name': 'Ergebnis', 'type': 'pie', 'radius': ['40%', '70%'],
                            'label': {'color': '#ffffff'},
                            'data': [
                                {'value': stats['player_wins'], 'name': 'Spieler', 'itemStyle': {'color': '#4ade80'}},
                                {'value': stats['dealer_wins'], 'name': 'Dealer', 'itemStyle': {'color': '#f87171'}},
                                {'value': stats['draws'], 'name': 'Unentschieden', 'itemStyle': {'color': '#facc15'}},
                            ]
                        }]
                    }).classes('w-full h-full')
                else:
                    ui.label('Keine Daten für Chart').classes('text-gray-500 mt-20 text-center w-full')

        games = db_manager.get_all_games(50)
        if not games:
            ui.label('Noch keine Spiele absolviert.').classes('text-gray-400 mt-4 text-xl')
        else:
            with ui.card().classes('w-full max-w-4xl bg-black/30 p-4 border border-white/10 rounded-2xl'):
                columns = [
                    {'name': 'time', 'label': 'Zeit', 'field': 'time', 'align': 'left', 'sortable': True},
                    {'name': 'winner', 'label': 'Gewinner', 'field': 'winner', 'align': 'center'},
                    {'name': 'player', 'label': 'Spieler (Punkte)', 'field': 'player', 'align': 'left'},
                    {'name': 'dealer', 'label': 'Dealer (Punkte)', 'field': 'dealer', 'align': 'left'},
                ]
                
                rows = []
                for g in games:
                    win_icon = '�' if g.winner == 'Spieler' else ('🔴' if g.winner == 'Dealer' else '⚪')
                    rows.append({
                        'time': g.timestamp.strftime('%d.%m.%Y %H:%M'),
                        'winner': f"{win_icon} {g.winner}",
                        'player': f"{g.player_score} PTS [{g.player_cards}]",
                        'dealer': f"{g.dealer_score} PTS [{g.dealer_cards}]",
                    })
                
                ui.table(columns=columns, rows=rows, row_key='time').classes('w-full bg-transparent text-white').props('dark flat')


# ============================================================================
# EINSTELLUNGEN (/settings)
# ============================================================================
@ui.page('/settings')
def render_settings() -> None:
    ui.query('body').style('margin: 0; padding: 0; background-color: #0f172a;')
    s = db_manager.get_settings()
    
    def save() -> None:
        db_manager.save_settings(
            show_hints=hint_sw.value,
            auto_stand_21=stand_sw.value,
            table_color=color_input.value
        )
        ui.notify('Einstellungen erfolgreich gespeichert!', color='positive')

    with ui.column().classes('w-full min-h-screen items-center py-6 px-4 text-white'):
        with ui.row().classes('w-full max-w-2xl justify-between items-center mb-6 bg-black/40 p-4 rounded-xl shadow-lg border border-white/5'):
            ui.button('← Menü', on_click=lambda: ui.navigate.to('/')).props('flat color=yellow')
            ui.label('Einstellungen').classes('text-2xl font-bold text-yellow-500 drop-shadow')
            ui.button('Speichern', on_click=save).props('color=green-700 unelevated')

        with ui.column().classes('w-full max-w-2xl gap-6'):
            # Gameplay Section
            with ui.card().classes('w-full bg-black/30 p-6 text-white border border-white/10 rounded-2xl shadow-lg'):
                with ui.row().classes('items-center mb-4 gap-2'):
                    ui.icon('videogame_asset', size='md').classes('text-yellow-500')
                    ui.label('Gameplay').classes('text-xl font-bold text-yellow-500')
                
                with ui.row().classes('w-full justify-between items-center py-3 border-b border-white/5'):
                    with ui.column().classes('gap-1'):
                        ui.label('Hilfestellungen anzeigen').classes('text-lg font-medium')
                        ui.label('Empfehlungen für Hit oder Stand basierend auf Punkten.').classes('text-sm text-gray-400')
                    hint_sw = ui.switch(value=s['show_hints']).props('color=green')

                with ui.row().classes('w-full justify-between items-center py-3'):
                    with ui.column().classes('gap-1'):
                        ui.label('Auto-Stand bei 21').classes('text-lg font-medium')
                        ui.label('Zieht keine weiteren Karten mehr, wenn 21 erreicht ist.').classes('text-sm text-gray-400')
                    stand_sw = ui.switch(value=s['auto_stand_21']).props('color=green')

            # Design Section
            with ui.card().classes('w-full bg-black/30 p-6 text-white border border-white/10 rounded-2xl shadow-lg'):
                with ui.row().classes('items-center mb-4 gap-2'):
                    ui.icon('palette', size='md').classes('text-yellow-500')
                    ui.label('Optik & Design').classes('text-xl font-bold text-yellow-500')

                with ui.row().classes('w-full justify-between items-center py-3'):
                    with ui.column().classes('gap-1'):
                        ui.label('Tischfarbe').classes('text-lg font-medium')
                        ui.label('Farbe des Hintergrunds am Spieltisch (Hex).').classes('text-sm text-gray-400')
                    
                    with ui.row().classes('items-center gap-2'):
                        color_preview = ui.element('div').classes('w-8 h-8 rounded shrink-0 border border-white/20 shadow-inner').style(f'background-color: {s["table_color"]}')
                        color_input = ui.input(value=s['table_color']).classes('w-32 text-lg').props('dense standout dark')
                        def update_color(e):
                            color_preview.style(f'background-color: {e.value}')
                        color_input.on('input', update_color)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='PyJack', favicon='🎰', dark=True)