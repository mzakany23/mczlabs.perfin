from assertpy import assert_that


def assert_helper(assertion, item, should_be):
    getattr(assert_that(item), assertion)(should_be)