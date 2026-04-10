from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class GameRecord(Base):
    """ORM-Modell fuer Spielhistorie."""
    __tablename__ = 'game_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    winner = Column(String(20), nullable=False)
    player_score = Column(Integer, nullable=False)
    dealer_score = Column(Integer, nullable=False)
    player_cards = Column(String(100), nullable=False)
    dealer_cards = Column(String(100), nullable=False)


class AppSettings(Base):
    """Persistente App-Einstellungen."""
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True, default=1)
    table_color = Column(String(30), default='#163824')
    card_back = Column(String(20), default='bg-blue-900')
    show_hints = Column(Boolean, default=True)
    animations = Column(Boolean, default=True)
    auto_stand_21 = Column(Boolean, default=True)


class DatabaseManager:
    """Verwaltet Datenbankverbindung und alle CRUD-Operationen."""

    def __init__(self, db_url: str = "sqlite:///pyjack.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def save_game(
        self,
        winner: str,
        player_score: int,
        dealer_score: int,
        player_cards: str,
        dealer_cards: str,
    ) -> None:
        session = self.get_session()
        try:
            session.add(GameRecord(
                winner=winner,
                player_score=player_score,
                dealer_score=dealer_score,
                player_cards=player_cards,
                dealer_cards=dealer_cards,
            ))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"DB-Fehler: {e}")
        finally:
            session.close()

    def get_all_games(self, limit: int = 10) -> List[GameRecord]:
        session = self.get_session()
        try:
            return (
                session.query(GameRecord)
                .order_by(GameRecord.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def get_all_games_asc(self) -> List[GameRecord]:
        session = self.get_session()
        try:
            return (
                session.query(GameRecord)
                .order_by(GameRecord.timestamp.asc())
                .all()
            )
        finally:
            session.close()

    def delete_all_games(self) -> None:
        session = self.get_session()
        try:
            session.query(GameRecord).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Reset-Fehler: {e}")
        finally:
            session.close()

    def get_statistics(self) -> dict:
        session = self.get_session()
        try:
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
        finally:
            session.close()

    def get_settings(self) -> dict:
        session = self.get_session()
        try:
            s = session.query(AppSettings).filter(AppSettings.id == 1).first()
            if s is None:
                s = AppSettings(id=1)
                session.add(s)
                session.commit()
                session.refresh(s)
            return {
                'table_color': s.table_color or '#163824',
                'card_back': s.card_back or 'bg-blue-900',
                'show_hints': s.show_hints if s.show_hints is not None else True,
                'animations': s.animations if s.animations is not None else True,
                'auto_stand_21': s.auto_stand_21 if s.auto_stand_21 is not None else True,
            }
        finally:
            session.close()

    def save_settings(self, **kwargs) -> None:
        session = self.get_session()
        try:
            s = session.query(AppSettings).filter(AppSettings.id == 1).first()
            if s is None:
                s = AppSettings(id=1)
                session.add(s)
            for key, value in kwargs.items():
                if hasattr(s, key):
                    setattr(s, key, value)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Settings-Fehler: {e}")
        finally:
            session.close()