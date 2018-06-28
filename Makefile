all: competition/scoring_program.zip competition/dev_data.zip competition/test_data.zip competition.zip submission.zip

competition/scoring_program.zip: scoring_program/*
	cd scoring_program && zip -r ../competition/scoring_program.zip * && cd ..

competition/dev_data.zip: dev_data/*
	cd dev_data && zip -r  ../competition/dev_data.zip * && cd ..

competition/test_data.zip: test_data/*
	cd test_data && zip -r  ../competition/test_data.zip * && cd ..

competition.zip: competition/* competition/scoring_program.zip competition/dev_data.zip competition/test_data.zip
	cd competition && zip -r  ../competition.zip * && cd ..

submission.zip: submission/*
	cd submission && zip -r ../submission.zip * && cd ..

clean:
	rm competition/scoring_program.zip competition/dev_data.zip competition/test_data.zip competition.zip submission.zip