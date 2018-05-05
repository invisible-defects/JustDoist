# coding: utf-8

# NOTE: Probably we need to write some kind of script
# that will create DB objects on startup.
class PredefinedProblems(object):
    problems = {
        2: {
            "uid": 2,
            "title": "Problem #2",
            "body": "Description",
        },
        3: {
            "uid": 3,
            "title": "Problem #3",
            "body": "Description",
        },
    }

    @staticmethod
    def get_problem(uid):
        return PredefinedProblems.problems[uid]
