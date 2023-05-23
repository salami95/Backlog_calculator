from aqt import mw
from aqt.utils import showInfo, getText
from PyQt5.QtWidgets import QAction
from datetime import datetime, timedelta, date
from typing import List
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QPushButton
import json
import traceback

def get_date():
    dialog = QDialog()
    layout = QVBoxLayout()
    calendar = QCalendarWidget()
    layout.addWidget(calendar)
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button)
    dialog.setLayout(layout)
    if dialog.exec_() == QDialog.Accepted:
        return calendar.selectedDate().toPyDate()
    else:
        return None

def calculate_backlog():
    # Get the collection
    col = mw.col

    # Ask the user for a deck name
    deck_name, ok = getText("Enter the name of the deck:")
    if not ok or not deck_name:
        return
    
    # Get the deck by name
    deck = col.decks.byName(deck_name)
    if deck is None:
        showInfo(f"No deck found with the name '{deck_name}'. Please enter the exact name of the deck.")
        return
    deck_id = deck['id']
    
    # Get the due cards for the specified deck until target date
    target_date = get_date()
    if target_date is None:
        return

    target_date_str = target_date.strftime("%Y-%m-%d")
    today = datetime.today()
    days_until_target = (target_date - today.date()).days + 1  # +1 to include today

    due_cards_per_day: List[int] = [0] * days_until_target
    card_ids = col.find_cards(f'"deck:{deck_name}" (is:due -prop:due=0)')  # use your search terms without asterisk
    for card_id in card_ids:
        card = col.getCard(card_id)
        try:
            if card.type == 1:  # learning card
                due_date = datetime.fromtimestamp(card.due) + timedelta(days=card.ivl)
                due_day = (due_date.date() - today.date()).days
                if 0 <= due_day < days_until_target:
                    due_cards_per_day[due_day] += 1
            elif card.type == 2:  # review card
                due_cards_per_day[0] += 1  # review cards are considered due immediately
        except Exception as e:
            showInfo(f"Error processing card with id {card_id}:\n{traceback.format_exc()}")

    # Calculate backlog
    backlog = sum(due_cards_per_day)
    
    # Calculate the number of cards that need to be reviewed per day
    cards_per_day = backlog // days_until_target

    showInfo(f"Your current card backlog is {backlog} cards. To finish by {target_date_str}, you need to review approximately {cards_per_day} cards per day.")

action = QAction("Calculate Backlog", mw)
action.triggered.connect(calculate_backlog)
mw.form.menuTools.addAction(action)
