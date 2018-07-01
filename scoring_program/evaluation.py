#!/usr/bin/env python3
import sys
import os.path
from semstr.evaluate import evaluate_all, Scores, passage_format, EVALUATORS, summarize
from ucca.evaluation import LABELED, UNLABELED

if __name__ == "__main__":
    # as per the metadata file, input and output directories are the arguments
    [_, input_dir, output_dir] = sys.argv
    submission_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')

    langs = ["English_in_domain", "English_out_of_domain", "German", "French"]
    tracks = ["open", "close"]

    competitions = [(lang, track) for lang in langs for track in tracks]
    competitions.remove(("French", "close"))

    with open(os.path.join(output_dir, 'scores.txt'), 'w') as output_file:
        with open(os.path.join(output_dir, 'scores.html'), 'w') as output_html_file:
            for (lang, track) in competitions:
                competition = lang + "_" + track
                if os.path.exists(submission_dir + "/" + competition):
                    print("Running evaluation on %s track" % (competition))

                    files = [[os.path.join(d, f) for f in os.listdir(d)] if os.path.isdir(d) else [d] for d in
                             (submission_dir + "/" + competition, truth_dir + "/" + competition)]
                    evaluate = EVALUATORS.get(passage_format(files[1][0])[1], EVALUATORS[None]).evaluate
                    results = list(evaluate_all(evaluate, files, format=None, unlabeled=False, matching_ids=True))
                    summary = Scores(results)
                    summarize(summary)

                    output_file.write("%s_averaged_labeled_f1: %.3f\n" % (competition, summary.average_f1(LABELED)))
                    output_html_file.write("######################\n")
                    output_html_file.write(
                        "%s_UCCA_averaged_labeled_f1: %.3f\n" % (competition, summary.average_f1(LABELED)))
                    for (title, field) in zip(summary.titles(LABELED), summary.fields(LABELED)):
                        output_html_file.write("%s_%s: %.3f\n" % (competition, title, float(field)))
                    output_file.write("%s_averaged_unlabeled_f1: %.3f\n" % (competition, summary.average_f1(UNLABELED)))
                    output_html_file.write("######################\n")
                    output_html_file.write(
                        "%s_UCCA_averaged_unlabeled_f1: %.3f\n" % (competition, summary.average_f1(UNLABELED)))
                    for (title, field) in zip(summary.titles(UNLABELED), summary.fields(UNLABELED)):
                        output_html_file.write("%s_%s: %.3f\n" % (competition, title, float(field)))

                else:
                    print("Results for %s track does not exists" % (competition))
