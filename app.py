import time
from flask import Flask, send_file, make_response
import parser
app = Flask(__name__) 

@app.route('/playbyplay/<date>')
def generate_csv(date):

    date_obj = time.strptime(date, "%m%d%Y")   
    date = time.strftime("%Y%m%d", date_obj)
    headers = { 'Content-Type': 'application/zip', 
                'Content-Disposition': 'attachment; filename=playbyplay_' + date +'.zip'}
    c = parser.Controller()
    files = c.generate_playbyplay_csv(date)
    zip_bytes = c.convert_to_bytes(files[0], files[1])
    return make_response(zip_bytes, 200, headers)


if __name__ == '__main__':
    app.run(debug=True)

