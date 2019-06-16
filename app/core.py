#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: core.py
# Quiz Bot: Game core (Model)

import data
from random import shuffle, randint


class Ticket(object):
    """
    Class containing information of single question instance
    """

    def __init__(self, database: data.QuestionsDB):
        self.questions_db = database
        self.question_id: int = None
        self.question: str = None
        self.correct_answer: str = None
        self.answers: list = None
        self.correct_answer_pos: int = None
        self.is_matched: bool = False

    def load(self, question_id: int):
        """
        Load data to the Ticket object from the Questions DB
        :param question_id: Question ID in the DB
        """
        row: tuple = self.questions_db.search_row_by_id(question_id)
        # row = (id, question, correct_answer, *answers)
        self.question_id = row[0]
        self.question = row[1]
        self.correct_answer = row[2]
        # Merge correct answer and extracted tuple of answers
        self.answers = [self.correct_answer, *row[3:]]
        shuffle(self.answers)
        # Position is a list index augmented once
        self.correct_answer_pos = (
            self.answers.index(self.correct_answer) + 1
        )


class Session(object):
    """
    Operational class
    """

    def __init__(self, user_id: int):
        self.hdb = data.HistoryDB()
        self.qdb = data.QuestionsDB()
        self.uid = user_id
        self.ticket = Ticket(self.qdb)

    def start(self):
        """
        Actions to start the game
        Modify ticket-properties to show them in Controller/View later
        Set game over if there are no more questions to propose
        """
        print("Start as:\t\t%s" % self.uid)
        # Question ID is a verified number of the next question
        question_id = self.choose_question()
        # If game ran out of questions
        if not question_id:
            # Set the variable that the game is finished for this user
            self.game_over = True
            return None
        # Load data to Ticket-instance and access the DB by question ID
        self.ticket.load(question_id)
        self.game_over = False

    def choose_question(self):
        """
        Choose a question ID to propose it as the next question
        Verify if it's not listed in User History DB
        :return: (int) Question row ID for further interaction with DB
        :return: (None) If history length >= questions length
        """
        self.__history: list = self.hdb.search_qnum_by_uid(self.uid)
        print("History:\t\t%s" % self.__history)
        # Calculate a user history length
        self.__hlen: int = len(self.__history)
        # Questions list length
        self.__qlen: int = len(self.qdb.select_all_rows())
        # Question left = Question length - History length
        self.__qleft: int = self.__qlen - self.__hlen
        print("Question left:\t\t%s" % self.__qleft)
        # If there is atleast 1 question left to propose it keeps going
        if self.__qleft:
            while True:
                rand_index: int = randint(1, self.__qlen)
                # If question ID is not listed in history yet then break
                if rand_index not in self.__history:
                    print("Rand number:\t\t%s" % rand_index)
                    return rand_index

    def finish(self, message_text: str):
        """
        Actions to finish the game
        Verify whether the answer is correct and set is_matched
        :param message_text: Text recieved from the user
        """
        print("Finish as:\t\t%s" % self.uid)
        print(
            "Right answer position:\t%s"
            % self.ticket.correct_answer_pos
        )
        if (message_text == self.ticket.correct_answer) or (
            message_text == str(self.ticket.correct_answer_pos)
        ):
            self.update_history()
            self.is_matched = True
        else:
            self.is_matched = False
        print("Is answer correct:\t%s" % self.is_matched)

    def update_history(self):
        """
        Update User History DB
        Insert user ID and question ID to the database
        """
        print("User History DB is updated!")
        self.hdb.insert_row(self.uid, self.ticket.question_id)
