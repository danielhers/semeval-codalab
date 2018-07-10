#!/usr/bin/env python3
import sys
import os.path
from semstr.evaluate import evaluate_all, Scores, passage_format, EVALUATORS, summarize
from ucca.evaluation import LABELED, UNLABELED
import yaml
from google.oauth2 import service_account
import googleapiclient.discovery

SERVICE_ACCOUNT_FILE = {}

PRACTICE_SPREADSHEET_ID = '1YXP22VAIVRtZngax0ZBuGCNYzprhAoxS46nr8n3mPcY'
EVALUATION_SPREADSHEET_ID = '1b3b5dKH18Qr0zHvPJdFP6KMMBU3jlKaRk_xYC5a7RjE'
POST_EVALUATION_SPREADSHEET_ID = '10wwmK25w13VlkKXBasIS1JJS4K6vG8DII2Lt6DOR0aU'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

if __name__ == "__main__":
    # as per the metadata file, input and output directories are the arguments
    [_, input_dir, output_dir] = sys.argv
    submission_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')

    langs = ["English_in_domain", "English_out_of_domain", "German", "French"]
    tracks = ["open", "closed"]

    # Setup the Sheets API
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)

    metadata = yaml.load(open(os.path.join(input_dir, 'metadata'), 'r'))
    for key, value in metadata.items():
        print(key + ': ')
        print(str(value) + '\n')

    if metadata["competition-phase"] == 1:
        SPREADSHEET_ID = PRACTICE_SPREADSHEET_ID
    elif metadata["competition-phase"] == 2:
        SPREADSHEET_ID = EVALUATION_SPREADSHEET_ID
    else:
        SPREADSHEET_ID = POST_EVALUATION_SPREADSHEET_ID

    competitions = [(lang, track) for lang in langs for track in tracks]
    competitions.remove(("French", "closed"))
    with open(os.path.join(output_dir, 'scores.txt'), 'w') as output_file:
        with open(os.path.join(output_dir, 'scores.html'), 'w') as output_html_file:
            # html style
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
            # table
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
                    values = [metadata["submitted-by"], metadata["competition-submission"],
                              metadata["submitted-at"].strftime("%d.%m.%Y")]
                    print("Running evaluation on %s track" % (competition))

                    # run evaluation
                    files = [[os.path.join(d, f) for f in os.listdir(d)] if os.path.isdir(d) else [d] for d in
                             (submission_dir + "/" + competition, truth_dir + "/" + competition)]
                    evaluate = EVALUATORS.get(passage_format(files[1][0])[1], EVALUATORS[None]).evaluate
                    results = list(evaluate_all(evaluate, files, format=None, unlabeled=False, matching_ids=True))
                    summary = Scores(results)
                    summarize(summary)

                    # write results to html file and append to values
                    output_html_file.write("<tr>\n"
                                           "<td>%s</td>" % competition)

                    # labeled
                    output_html_file.write("<td>%.3f</td>\n" % (summary.average_f1(LABELED)))
                    values.append(round(summary.average_f1(LABELED), 3))
                    for (title, field) in zip(summary.titles(LABELED), summary.fields(LABELED)):
                        output_html_file.write("<td>%.3f</td>\n" % (float(field)))
                        values.append(float(field))

                    # unlabeled
                    output_html_file.write("<td>%.3f</td>\n" % (summary.average_f1(UNLABELED)))
                    values.append(round(summary.average_f1(UNLABELED), 3))
                    for (title, field) in zip(summary.titles(UNLABELED), summary.fields(UNLABELED)):
                        output_html_file.write("<td>%.3f</td>\n" % (float(field)))
                        values.append(float(field))
                    output_html_file.write("</tr>\n")

                    # write results to google sheet
                    body = {
                        'values': [values, ]
                    }
                    result = service.spreadsheets().values().append(
                        spreadsheetId=SPREADSHEET_ID, range=competition,
                        valueInputOption="RAW", body=body).execute()
                    print('{0} cells appended.'.format(result \
                                                       .get('updates') \
                                                       .get('updatedCells')))
                else:
                    print("Results for %s track does not exists" % (competition))

            output_file.write("correct: 1\n")

            output_html_file.write("<p> To see all results, have a look"
                                   "<a href='https://docs.google.com/spreadsheets/d/" + SPREADSHEET_ID + "'> here </a>.</p>")
            output_html_file.write("</tbody>\n"
                                   "</table>\n"
                                   "</body>\n"
                                   "</html>")
