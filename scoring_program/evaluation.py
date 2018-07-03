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
    tracks = ["open", "closed"]

    competitions = [(lang, track) for lang in langs for track in tracks]
    competitions.remove(("French", "closed"))
    seen_langs = []
    with open(os.path.join(output_dir, 'scores.txt'), 'w') as output_file:
        with open(os.path.join(output_dir, 'scores.html'), 'w') as output_html_file:

            output_html_file.write("<!DOCTYPE html>\n"
                                   "<html>\n"
                                   "<head>\n"
                                   "<style>\n"
                                    "table {\n"
                                       "font-family: Tahoma, Geneva, sans-serif;\n"
                                       "border: 0px solid #000000;\n"
                                       "width: 350px;\n"
                                       "height: 200px;\n"
                                       "text-align: center;\n"
                                       "border-collapse: collapse;\n"
                                    "}\n"
                                     "td, th {\n"
                                          "border: 1px solid #000000;\n"
                                         "padding: 3px 2px;\n"
                                    "}\n"
                                    "tbody td {\n"
                                        "font-size: 13px;\n"
                                    "}\n"


                                   "thead {\n"
                                   "background: #0B6FA4;\n"
                                   "border-bottom: 5px solid #000000;\n"
                                    "}\n"
                                    "thead th {\n"
                                   "font-size: 14px;\n"
                                   "font-weight: bold;\n"
                                   "color: #FFFFFF;\n"
                                   "text-align: center;\n"
                                   "border-left: 2px solid #000000;\n"
                                "}\n"
                                    "</style>\n"
                                   "<title>Detailed Results</title>\n"
                                   "</head>\n"
                                   "<body>\n")

            output_html_file.write('<table style="width:100%">\n'
                                    '<thead>\n'
                                    '<tr>\n'
                                   '<th rowspan="3">Track</th>\n'
                                   '<th colspan="7">Labeled</th>\n'
                                   '<th colspan="7">Unlabeled</th>\n'
                                   '</tr>\n'
                                    '<tr>\n'
                                    '<th rowspan="2">Averaged F1</th>\n'
                                   '<th colspan="3">Primary</th>\n'
                                   '<th colspan="3">Remote</th>\n'
                                    '<th rowspan="2">Averaged F1</th>\n'
                                    '<th colspan="3">Primary</th>\n'
                                   '<th colspan="3">Remote</th>\n'
                                   '</tr>\n'
                                    '<tr>\n'
                                   '<th>P</th>\n'
                                    '<th>R</th>\n'
                                    '<th>F1</th>\n'
                                    '<th>P</th>\n'
                                    '<th>R</th>\n'
                                    '<th>F1</th>\n'
                                   '<th>P</th>\n'
                                    '<th>R</th>\n'
                                    '<th>F1</th>\n'
                                    '<th>P</th>\n'
                                    '<th>R</th>\n'
                                    '<th>F1</th>\n'
                                   '</tr>\n'
                                   '</thead>\n'
                                   '<tbody>\n')


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
                    if lang not in seen_langs:
                        seen_langs.append(lang)
                        output_file.write("submitted_%s: 1\n" % (lang))


                    output_file.write("%s_averaged_labeled_f1: %.3f\n" % (competition, summary.average_f1(LABELED)))
                    output_html_file.write("<tr>\n"
                                           "<td>%s</td>" % competition)
                    output_html_file.write(
                        "<td>%.3f</td>\n" % (summary.average_f1(LABELED)))
                    for (title, field) in zip(summary.titles(LABELED), summary.fields(LABELED)):
                        output_html_file.write( "<td>%.3f</td>\n" % (float(field)))

                    output_file.write("%s_averaged_unlabeled_f1: %.3f\n" % (competition, summary.average_f1(UNLABELED)))


                    output_html_file.write(
                        "<td>%.3f</td>\n" % (summary.average_f1(UNLABELED)))
                    for (title, field) in zip(summary.titles(UNLABELED), summary.fields(UNLABELED)):
                        output_html_file.write("<td>%.3f</td>\n" % ( float(field)))
                    output_html_file.write("</tr>\n")
                else:
                    print("Results for %s track does not exists" % (competition))

            for lang in langs:
                if lang not in seen_langs:
                    output_file.write("submitted_%s: 0\n" % (lang))

            output_html_file.write("</tbody>\n"
                                   "</table>\n"
                                   "</body>\n"
                                   "</html>")