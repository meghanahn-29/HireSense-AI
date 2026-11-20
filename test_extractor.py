from skill_matcher import calculate_skill_match


# ==========================================
# HIRESENSE AI - SKILL MATCHING TESTS
# ==========================================

job_skills = [
    ("Python", True),
    ("Flask", True),
    ("MySQL", True),
    ("JavaScript", True),
    ("HTML", False),
    ("CSS", False)
]


test_cases = [

    {
        "name": "Highly Relevant Candidate",
        "skills": ["Python", "Flask", "MySQL", "JavaScript"],
        "expected_score": 100.0
    },

    {
        "name": "Partially Relevant Candidate",
        "skills": ["Python", "Flask"],
        "expected_score": 50.0
    },

    {
        "name": "Unrelated Candidate",
        "skills": ["Java", "C++"],
        "expected_score": 0.0
    },

    {
        "name": "Preferred Skills Only",
        "skills": ["HTML", "CSS"],
        "expected_score": 0.0
    },

    {
        "name": "Candidate With All Skills",
        "skills": [
            "Python", "Flask", "MySQL",
            "JavaScript", "HTML", "CSS"
        ],
        "expected_score": 100.0
    },

    {
        "name": "Skill Alias Test",
        "skills": ["Python", "Flask", "MySQL", "JS"],
        "expected_score": 100.0
    },

    {
        "name": "Negative Context Extraction Result",
        "skills": [],
        "expected_score": 0.0
    }

]


passed = 0
failed = 0

for test in test_cases:

    result = calculate_skill_match(
        test["skills"],
        job_skills
    )

    actual_score = result["skill_match_score"]

    print("\nTest:", test["name"])
    print("Candidate Skills:", test["skills"])
    print("Skill Match Score:", actual_score, "%")
    print("Missing Required Skills:",
          result["missing_required_skills"])

    if actual_score == test["expected_score"]:
        print("Status: PASS")
        passed += 1

    else:
        print("Status: FAIL")
        print("Expected:", test["expected_score"])
        failed += 1


print("\n========== TEST SUMMARY ==========")
print("Total Tests:", len(test_cases))
print("Passed:", passed)
print("Failed:", failed)
print("==================================")