# -*- coding: utf-8 -*-
#
# Copyright 2016 INVITE Communications Co., Ltd. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import mysql.connector
import logging


logger = logging.getLogger('survey.model')


class SurveyModel:
    """Database storage layer for the survey"""

    _project = None  # type: str
    """Name of the survey in the source database"""
    _id = None  # type: str|int
    """ID of the survey in the stats table (aka 'warlist')"""

    _source_db = None  # type: mysql.connector.MySQLConnection
    _destination_db = None  # type: mysql.connector.MySQLConnection

    _details = None  # type: dict
    """Survey parameters"""

    _questions = None  # type: dict
    """Parameters for all questions in the survey: {question: label}"""

    _question_answers = None  # type: dict
    """Valid answers for all questions in the survey: {question: { digit: next_question, ... } }"""

    def __init__(self, source_db, destination_db, project, id):
        """
        :param source_db:      Source database connection (read-only)
        :type  source_db:      mysql.connector.MySQLConnection
        :param destination_db: Connection to the database for collected survey stats (writable)
        :type  destination_db: mysql.connector.MySQLConnection
        :param project:        Name of the survey in the source database
        :type  project:        str
        :param id:             ID of the survey in the stats table (aka 'warlist')
        :type  id:             str|int
        """
        self._source_db = source_db
        self._destination_db = destination_db
        self._project = project
        self._id = id

    def get_details(self):
        """
        Get survey parameters
        """
        if self._details is None:
            self._details = self._query(
                'SELECT `intro_id`, `hangup_id`, `next` FROM `survey_details` WHERE `project` = %s',
                [self._project]
            )[0]
        return self._details

    def get_question_label(self, question_id):
        """
        Get label (field name) used for questions in the project table
        """
        if self._questions is None:
            self._questions = dict((row['question'], row['question_label']) for row in self._query('SELECT `question`, `question_label` FROM `survey_questions` WHERE `project` = %s', [self._project]))

        return self._questions[question_id]
        # return ''.join(results[0].values())  # Use JOIN to fix UTF8  # TODO why the join()?

    def get_valid_digits(self, question_id):
        """
        Get the list of valid digits for a question

        :rtype: List[str]
        """
        if not self._question_answers:
            self._get_all_valid_digits()

        return self._question_answers[question_id].keys()

    def get_next_question(self, current_question_id, entered_digit):
        """
        Get next question based on entered DTMF
        """
        if not self._question_answers:
            self._get_all_valid_digits()

        return self._question_answers[current_question_id][entered_digit]
        # return ''.join(results[0].values())  # Use JOIN to fix UTF8  # TODO why the join()?

    def _get_all_valid_digits(self):
        """
        Gets the list of valid digits for all question in the current survey
        """
        result = {}
        for row in self._query(
                'SELECT `question`, `dtmf`, `dtmf_next` FROM `survey_questions_dtmf` WHERE `project` = %s',
                [self._project]):
            if row['question'] not in result: result[row['question']] = {}
            result[row['question']][row['dtmf']] = row['dtmf_next']
        self._question_answers = result

    def update(self, parameters):
        """
        Write survey results in the destination database

        :param parameters: A dictionary of fields to update
        :type  parameters: dict
        """
        fields_sql = [ '`{0}` = %({0})s'.format(field) for field in parameters.keys() ]
        parameters['id'] = self._id

        cursor = self._destination_db.cursor()
        try:
            cursor.execute('UPDATE `' + self._project + '` SET ' + ', '.join(fields_sql) + ' WHERE id = %(id)s', parameters)
        finally:
            logger.debug('Executed MySQL query: %s', cursor._executed)

    def _query(self, query, params=None):
        cursor = self._source_db.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            logger.debug('Executed MySQL query: %s', cursor._executed)
