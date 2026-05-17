import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod

class CardRank(Enum):
    """Enum für alle 13 Kartenwerte im Blackjack inkl. Symbol und Basiswert."""
    TWO = ('2', 2)
    THREE = ('3', 3)
    FOUR = ('4', 4)
    FIVE = ('5', 5)
    SIX = ('6', 6)
    SEVEN = ('7', 7)
    EIGHT = ('8', 8)
    NINE = ('9', 9)
    TEN = ('10', 10)
    JACK = ('J', 10)
    QUEEN = ('Q', 10)
    KING = ('K', 10)
    ACE = ('A', 11)

    def __init__(self, symbol: str, value: int):
        self.symbol = symbol
        self.base_value = value


class CardSuit(Enum):
    """Enum für die vier Kartenfarben mit Unicode-Symbol und Farbbezeichnung."""
    HEARTS = ('\u2665', 'red')
    DIAMONDS = ('\u2666', 'red')
    CLUBS = ('\u2663', 'black')
    SPADES = ('\u2660', 'black')

    def __init__(self, symbol: str, color: str):
        self.symbol = symbol
        self.color = color


@dataclass
class Card:
    """Repräsentiert eine einzelne Spielkarte mit Rang und Farbe."""
    rank: CardRank
    suit: CardSuit

    def __str__(self) -> str:
        return f"{self.rank.symbol}{self.suit.symbol}"

    def __repr__(self) -> str:
        return f"Card(rank={self.rank!r}, suit={self.suit!r})"

    def get_display_value(self) -> int:
        return self.rank.base_value

    def is_ace(self) -> bool:
        return self.rank == CardRank.ACE


class Deck:
    """Repräsentiert ein vollständiges Kartenspiel mit 52 gemischten Karten."""
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def __repr__(self) -> str:
        return f"Deck(remaining={len(self.cards)} cards)"

    def reset(self) -> None:
        """Setzt das Deck zurück: erstellt alle 52 Karten neu und mischt sie."""
        self.cards = [Card(r, s) for r in CardRank for s in CardSuit]
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        """Zieht die oberste Karte vom Deck.
        
        Returns:
            Optional[Card]: Eine Karte oder None falls das Deck leer ist.
        """
        return self.cards.pop() if self.cards else None


class Hand:
    """Verwaltet die Karten und den Punktwert einer Spielerhand."""
    def __init__(self):
        self.cards: List[Card] = []

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards!r}, value={self.get_value()})"

    def add_card(self, card: Card) -> None:
        if card:
            self.cards.append(card)

    def get_value(self) -> int:
        """Berechnet den Handwert nach Blackjack-Regeln (Asse flexibel 1 oder 11).
        
        Returns:
            int: Handwert, maximal 21 ohne Bust.
        """
        total = sum(c.get_display_value() for c in self.cards)
        aces = sum(1 for c in self.cards if c.is_ace())
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def is_bust(self) -> bool:
        return self.get_value() > 21

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.get_value() == 21

    def clear(self) -> None:
        self.cards.clear()

    def get_cards_string(self) -> str:
        return ', '.join(str(c) for c in self.cards)


class Player(ABC):
    """Basisklasse für einen Blackjack-Spieler mit Hand und Aktionen."""
    def __init__(self, name: str = "Spieler"):
        self.name = name
        self._hand = Hand()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, score={self.get_score()})"

    @property
    def hand(self) -> Hand:
        """Gibt die aktuelle Hand des Spielers zurück (read-only)."""
        return self._hand

    def reset_hand(self) -> None:
        self._hand.clear()

    def receive_card(self, card: Card) -> None:
        self._hand.add_card(card)

    def get_score(self) -> int:
        return self._hand.get_value()

    @abstractmethod
    def should_draw(self) -> bool:
        """Determines whether this participant should draw another card."""
        return False


class HumanPlayer(Player):
    """Konkrete Implementierung für den menschlichen Spieler."""
    def should_draw(self) -> bool:
        return False


class Dealer(Player):
    """Dealer-Klasse mit automatischer Zuglogik und verdeckter Erstkarte."""
    def __init__(self):
        super().__init__(name="Dealer")
        self.hide_first_card = True

    def __repr__(self) -> str:
        return f"Dealer(score={self.get_score()}, hidden={self.hide_first_card})"

    def should_draw(self) -> bool:
        return self.get_score() < 17

    def reveal_cards(self) -> None:
        self.hide_first_card = False

    def get_visible_score(self) -> int:
        if self.hide_first_card and len(self._hand.cards) >= 2:
            return self._hand.cards[1].get_display_value()
        return self.get_score()


class GameState(Enum):
    """Enum für die vier möglichen Spielzustände."""
    WAITING = 'Warten'
    PLAYER_TURN = 'Spieler'
    DEALER_TURN = 'Dealer'
    GAME_OVER = 'Beendet'


class Winner(Enum):
    """Enum für die drei möglichen Rundenausgänge."""
    PLAYER = "Spieler"
    DEALER = "Dealer"
    DRAW   = "Unentschieden"


class Game:
    """Steuert den vollständigen Spielablauf einer Blackjack-Runde."""
    def __init__(self):
        self.deck = Deck()
        self.player = HumanPlayer()
        self.dealer = Dealer()
        self.state = GameState.WAITING
        self.winner: Optional[Winner] = None
        self.last_result: Optional[dict] = None

    def start_new_game(self) -> None:
        self.deck.reset()
        self.player.reset_hand()
        self.dealer.reset_hand()
        self.dealer.hide_first_card = True
        self.state = GameState.PLAYER_TURN
        self.winner = None
        self.last_result = None

        for _ in range(2):
            if player_card := self.deck.draw():
                self.player.receive_card(player_card)
            if dealer_card := self.deck.draw():
                self.dealer.receive_card(dealer_card)

        if self.player.hand.is_blackjack():
            self.dealer.reveal_cards()
            self.end_game(Winner.DRAW if self.dealer.hand.is_blackjack() else Winner.PLAYER)

    def player_hit(self) -> None:
        if self.state != GameState.PLAYER_TURN:
            return
        card = self.deck.draw()
        if card:
            self.player.receive_card(card)
        if self.player.hand.is_bust():
            self.end_game(Winner.DEALER)

    def player_stand(self) -> None:
        if self.state != GameState.PLAYER_TURN:
            return
        self.state = GameState.DEALER_TURN
        self.dealer.reveal_cards()
        self.play_dealer_turn()

    def play_dealer_turn(self) -> None:
        while self.dealer.should_draw():
            card = self.deck.draw()
            if card:
                self.dealer.receive_card(card)
            else:
                break
        self.determine_winner()

    def determine_winner(self) -> None:
        ps = self.player.get_score()
        ds = self.dealer.get_score()
        if ds > 21:
            winner = Winner.PLAYER
        elif ps > ds:
            winner = Winner.PLAYER
        elif ps < ds:
            winner = Winner.DEALER
        else:
            winner = Winner.DRAW
        self.end_game(winner)

    def end_game(self, winner: Winner) -> None:
        self.state = GameState.GAME_OVER
        self.winner = winner
        self.dealer.reveal_cards()
        self.last_result = {
            'winner': winner.value,
            'player_score': self.player.get_score(),
            'dealer_score': self.dealer.get_score(),
            'player_cards': self.player.hand.get_cards_string(),
            'dealer_cards': self.dealer.hand.get_cards_string()
        }

    def can_player_act(self) -> bool:
        return self.state == GameState.PLAYER_TURN