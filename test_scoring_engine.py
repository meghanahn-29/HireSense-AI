from scoring_engine import calculate_overall_score


test_cases = [
    ("Highly Relevant", 90, 85, 90),
    ("Partially Relevant", 60, 50, 65),
    ("Unrelated Resume", 10, 5, 15),
    ("Zero Scores", 0, 0, 0),
    ("Perfect Scores", 100, 100, 100),

    # Previous actual project test
    ("Previous Sample", 100, 7.43, 49.67)
]


print("\n========== HIRESENSE AI ==========")
print("       OVERALL SCORING TEST")
print("==================================\n")


for name, skill, tfidf, semantic in test_cases:

    overall_score = calculate_overall_score(
        skill,
        tfidf,
        semantic
    )

    print(f"{name}")
    print(f"Skill Match Score: {skill}")
    print(f"TF-IDF Score: {tfidf}")
    print(f"SBERT Score: {semantic}")
    print(f"Overall Score: {overall_score}%")
    print("----------------------------------")


print("\nAll scoring tests completed.")