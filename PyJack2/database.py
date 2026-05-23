from datetime import datetime
from typing import List, Any
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class GameRecord(Base):
    """ORM-Modell für einen abgeschlossenen Spielverlauf."""
    __tablename__ = 'game_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    winner = Column(String(20), nullable=False)
    player_score = Column(Integer, nullable=False)
    dealer_score = Column(Integer, nullable=False)
    player_cards = Column(String(100), nullable=False)
    dealer_cards = Column(String(100), nullable=False)


class AppSettings(Base):
    """Persistente Benutzereinstellungen der Anwendung (Singleton, id=1)."""
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True, default=1)
    table_color = Column(String(30), default='#163824')
    card_back = Column(String(20), default='#1e3a8a')
    show_hints = Column(Boolean, default=True)
    auto_stand_21 = Column(Boolean, default=True)


class DatabaseManager:
    """Verwaltet die SQLite-Datenbankverbindung und alle CRUD-Operationen."""

    def __init__(self, db_url: str = "sqlite:///pyjack.db"):
        """Initialisiert die Datenbankverbindung und erstellt Tabellen falls nötig.
        
        Args:
            db_url: SQLAlchemy-Verbindungs-URL. Standard: lokale SQLite-Datei.
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self) -> Session:
        """Gibt eine neue Datenbank-Session zurück.
        
        Returns:
            Ein Session-Objekt für Datenbankoperationen.
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """Context manager that provides a transactional database session.
        
        Yields:
            Session: An active SQLAlchemy session. Commits on success,
                     rolls back on exception, always closes.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Session rollback due to: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def save_game(
        self,
        winner: str,
        player_score: int,
        dealer_score: int,
        player_cards: str,
        dealer_cards: str,
    ) -> None:
        """Speichert einen abgeschlossenen Spielverlauf in der Datenbank.
        
        Args:
            winner: Gewinner als String ('Spieler', 'Dealer', 'Unentschieden').
            player_score: Endpunktzahl des Spielers.
            dealer_score: Endpunktzahl des Dealers.
            player_cards: Karten des Spielers als kommagetrennte Zeichenkette.
            dealer_cards: Karten des Dealers als kommagetrennte Zeichenkette.
        """
        with self.session_scope() as session:
            session.add(GameRecord(
                winner=winner,
                player_score=player_score,
                dealer_score=dealer_score,
                player_cards=player_cards,
                dealer_cards=dealer_cards,
            ))

    def get_all_games(self, limit: int = 10) -> List[GameRecord]:
        """Gibt die neuesten Spieleinträge absteigend nach Zeitstempel zurück.
        
        Args:
            limit: Maximale Anzahl zurückgegebener Einträge.
        Returns:
            Liste von GameRecord-Objekten.
        """
        with self.session_scope() as session:
            return (
                session.query(GameRecord)
                .order_by(GameRecord.timestamp.desc())
                .limit(limit)
                .all()
            )

    def get_all_games_asc(self) -> List[GameRecord]:
        """Gibt alle Spieleinträge aufsteigend nach Zeitstempel zurück.
        
        Returns:
            Liste von GameRecord-Objekten.
        """
        with self.session_scope() as session:
            return (
                session.query(GameRecord)
                .order_by(GameRecord.timestamp.asc())
                .all()
            )

    def delete_all_games(self) -> None:
        """Löscht alle Spielhistorien-Einträge aus der Datenbank."""
        with self.session_scope() as session:
            session.query(GameRecord).delete()

    def get_statistics(self) -> dict[str, Any]:
        """Berechnet Spielstatistiken basierend auf der Historie.
        
        Returns:
            Dictionary mit Gesamtzahl, Siegen, Niederlagen, Unentschieden und Gewinnrate.
        """
        with self.session_scope() as session:
            total = session.query(GameRecord).count()
            pw = session.query(GameRecord).filter(GameRecord.winner == 'Spieler').count()
            dw = session.query(GameRecord).filter(GameRecord.winner == 'Dealer').count()
            dr = session.query(GameRecord).filter(GameRecord.winner == 'Unentschieden').count()
            return {
                'total_games': total,
                'player_wins': pw,
                'dealer_wins': dw,
                'draws': dr,
                'player_win_rate': (pw / total * 100) if total > 0 else 0.0,
            }

    def get_settings(self) -> dict[str, Any]:
        """Lädt die aktuellen App-Einstellungen oder erstellt Standardwerte.
        
        Returns:
            Dictionary mit den aktuellen Einstellungen.
        """
        with self.session_scope() as session:
            s = session.query(AppSettings).filter(AppSettings.id == 1).first()
            if s is None:
                s = AppSettings(id=1)
                session.add(s)
                session.commit()
                session.refresh(s)
            return {
                'table_color': s.table_color or '#163824',
                'card_back': s.card_back or '#1e3a8a',
                'show_hints': s.show_hints if s.show_hints is not None else True,
                'auto_stand_21': s.auto_stand_21 if s.auto_stand_21 is not None else True,
            }

    def save_settings(self, **kwargs) -> None:
        """Speichert übergebene Einstellungswerte in der Datenbank.
        
        Args:
            **kwargs: Schlüssel-Wert-Paare der zu speichernden Einstellungen.
        """
        with self.session_scope() as session:
            s = session.query(AppSettings).filter(AppSettings.id == 1).first()
            if s is None:
                s = AppSettings(id=1)
                session.add(s)
            for key, value in kwargs.items():
                if hasattr(s, key):
                    setattr(s, key, value)