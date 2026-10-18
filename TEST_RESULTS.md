# My test results

## Environment
Python version: 3.14.8
Operating system: Windows 11 Home (10.0.26300)

## Automated tests
Command: `python -m unittest discover -s tests -v`
Number passed: 48
Number failed: 0
What I learned: _(write this in your own words)_

| Test file | What it checks | Tests | Result |
|---|---|---|---|
| `tests/test_rules.py` | Original 60-day renewal rule | 4 | all ok |
| `tests/test_store.py` | Original fake data setup | 1 | ok |
| `tests/test_search.py` | Feature A: `GET /api/trainees?course=` search | 10 | all ok |
| `tests/test_register.py` | Feature B: `POST /api/trainees` registration, including "no expiry date before today" | 26 | all ok |
| `tests/test_courses.py` | `GET /api/courses` list, and registration only allowed for existing courses | 7 | all ok |

All tests use a temporary database, so the real `courseflow.sqlite3` is never touched.

### Test output
```
test_get_courses (test_courses.ApiCourseTests.test_get_courses) ... ok
test_post_with_different_capitalisation_returns_400 (test_courses.ApiCourseTests.test_post_with_different_capitalisation_returns_400) ... ok
test_post_with_existing_course_returns_201 (test_courses.ApiCourseTests.test_post_with_existing_course_returns_201) ... ok
test_post_with_unknown_course_returns_400_and_saves_nothing (test_courses.ApiCourseTests.test_post_with_unknown_course_returns_400_and_saves_nothing) ... ok
test_read_courses_is_unique_and_alphabetical (test_courses.CourseListTests.test_read_courses_is_unique_and_alphabetical) ... ok
test_existing_course_accepted (test_courses.CourseRuleTests.test_existing_course_accepted) ... ok
test_unknown_course_rejected (test_courses.CourseRuleTests.test_unknown_course_rejected) ... ok
test_blank_name_returns_400_and_saves_nothing (test_register.ApiRegisterTests.test_blank_name_returns_400_and_saves_nothing) ... ok
test_broken_json_returns_400 (test_register.ApiRegisterTests.test_broken_json_returns_400) ... ok
test_invalid_expiry_returns_400 (test_register.ApiRegisterTests.test_invalid_expiry_returns_400) ... ok
test_json_that_is_not_an_object_returns_400 (test_register.ApiRegisterTests.test_json_that_is_not_an_object_returns_400) ... ok
test_negative_content_length_returns_400 (test_register.ApiRegisterTests.test_negative_content_length_returns_400) ... ok
test_new_trainee_gets_renewal_badge (test_register.ApiRegisterTests.test_new_trainee_gets_renewal_badge) ... ok
test_null_expiry_returns_201 (test_register.ApiRegisterTests.test_null_expiry_returns_201) ... ok
test_past_expiry_returns_400_and_saves_nothing (test_register.ApiRegisterTests.test_past_expiry_returns_400_and_saves_nothing) ... ok
test_post_to_other_path_returns_404 (test_register.ApiRegisterTests.test_post_to_other_path_returns_404) ... ok
test_saved_trainee_appears_in_later_get (test_register.ApiRegisterTests.test_saved_trainee_appears_in_later_get) ... ok
test_today_expiry_returns_201 (test_register.ApiRegisterTests.test_today_expiry_returns_201) ... ok
test_too_large_body_returns_413 (test_register.ApiRegisterTests.test_too_large_body_returns_413) ... ok
test_valid_post_returns_201_with_id (test_register.ApiRegisterTests.test_valid_post_returns_201_with_id) ... ok
test_add_returns_record_with_new_id (test_register.StoreAddTests.test_add_returns_record_with_new_id) ... ok
test_added_trainee_is_saved (test_register.StoreAddTests.test_added_trainee_is_saved) ... ok
test_blank_course_rejected (test_register.ValidationTests.test_blank_course_rejected) ... ok
test_blank_name_rejected (test_register.ValidationTests.test_blank_name_rejected) ... ok
test_future_expiry_accepted (test_register.ValidationTests.test_future_expiry_accepted) ... ok
test_invalid_expiry_rejected (test_register.ValidationTests.test_invalid_expiry_rejected) ... ok
test_missing_name_rejected (test_register.ValidationTests.test_missing_name_rejected) ... ok
test_name_longer_than_100_characters_rejected (test_register.ValidationTests.test_name_longer_than_100_characters_rejected) ... ok
test_non_text_name_rejected (test_register.ValidationTests.test_non_text_name_rejected) ... ok
test_null_or_missing_expiry_means_no_expiry (test_register.ValidationTests.test_null_or_missing_expiry_means_no_expiry) ... ok
test_past_expiry_rejected (test_register.ValidationTests.test_past_expiry_rejected) ... ok
test_today_expiry_accepted (test_register.ValidationTests.test_today_expiry_accepted) ... ok
test_valid_data_is_accepted_and_trimmed (test_register.ValidationTests.test_valid_data_is_accepted_and_trimmed) ... ok
test_60_days_included (test_rules.RenewalTests.test_60_days_included) ... ok
test_61_days_excluded (test_rules.RenewalTests.test_61_days_excluded) ... ok
test_expired_not_upcoming (test_rules.RenewalTests.test_expired_not_upcoming) ... ok
test_missing_never_warned (test_rules.RenewalTests.test_missing_never_warned) ... ok
test_get_unknown_course (test_search.ApiSearchTests.test_get_unknown_course) ... ok
test_get_with_course_filter (test_search.ApiSearchTests.test_get_with_course_filter) ... ok
test_get_with_encoded_space (test_search.ApiSearchTests.test_get_with_encoded_space) ... ok
test_get_without_filter (test_search.ApiSearchTests.test_get_without_filter) ... ok
test_blank_filter_returns_all (test_search.StoreSearchTests.test_blank_filter_returns_all) ... ok
test_case_insensitive (test_search.StoreSearchTests.test_case_insensitive) ... ok
test_no_filter_returns_all (test_search.StoreSearchTests.test_no_filter_returns_all) ... ok
test_partial_match (test_search.StoreSearchTests.test_partial_match) ... ok
test_unknown_course_returns_empty_list (test_search.StoreSearchTests.test_unknown_course_returns_empty_list) ... ok
test_wildcard_characters_are_literal (test_search.StoreSearchTests.test_wildcard_characters_are_literal) ... ok
test_five_fake_trainees_in_isolated_database (test_store.StorageTests.test_five_fake_trainees_in_isolated_database) ... ok

----------------------------------------------------------------------
Ran 48 tests in 11.783s

OK
```

## Manual checks
_(tick each box after you have done it yourself at http://localhost:8765)_
- [ ] Filter for `refresher` (screenshot 1)
- [ ] Register a fictional trainee (screenshot 2)
- [ ] Refresh and check persistence
- [ ] Try an expiry date before today: red "Select valid date" appears and no row is added
- [ ] Course is a dropdown of existing courses; leaving it on "Select a course" shows red "Course is required"

## Bug I found and fixed
Problem: The original test `test_five_fake_trainees_in_isolated_database` failed on Windows with `PermissionError: [WinError 32]`. `store.py` never closed its SQLite connections: `with sqlite3.connect(...)` only saves (commits) the changes and leaves the connection open. Windows will not delete a file that is still open, so the test could not remove its temporary database.

How I noticed: The full test run showed the error. Running the same steps with the original, unchanged `store.py` code failed the same way, so the bug was in the starter, not in the search feature. Running with `python -W always::ResourceWarning` printed `ResourceWarning: unclosed database`, which pointed to the cause.

What I changed: In `store.py`, each connection is now wrapped in `contextlib.closing(...)`, which closes it as soon as the work is done. The new tests also stopped ignoring temporary-file cleanup errors, so they would catch this leak if it came back.

What test proves it is fixed: `test_five_fake_trainees_in_isolated_database` now passes, together with every `test_search.py` and `test_register.py` test, each of which creates and deletes its own temporary database.

## What I still do not understand
_(write this in your own words)_
