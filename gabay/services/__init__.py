"""SERVICES layer (proposal section 2.3): the smart features, kept apart so they can be improved
without touching the rest of the system.

Not built yet: summary_generator, pass_score_calculator, pattern_detector, risk_scorer, qr_verifier.
Each one goes here as a plain Python file with no request, page, or database-query code;
a controller calls it and passes the result to a view.
"""
