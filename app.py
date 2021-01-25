import sys
from flask import Flask, render_template, request, redirect, jsonify
from db import DB
from iroha_engine import IrohaEngine

app = Flask(__name__)
swift = DB()
chain = IrohaEngine()
test_data = list()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=['POST', 'GET'])
def create_page():
    if request.method == 'POST':
        try:
            num = int(request.form["entries"])                      # type: int
            if num >= 0:
                swift.populate(num)
                return redirect(request.url)
            else:
                print("Value is not a valid number")
        except Exception as e:
            print(f"Exception {e} occurred")
            tb = sys.exc_info()
            return e.with_traceback(tb)
    else:
        return render_template('create.html')


@app.route('/db')
def db_transactions_page():
    results = swift.list_all()                                      # type: list
    return render_template('db_transactions.html', data=results)


@app.route('/hl')
def hl_transactions_page():
    results = chain.list_all()                                      # type: list
    return render_template('hl_transactions.html', data=results)


@app.route('/search', methods=['POST', 'GET'])
def search_page():
    if request.method == 'POST':
        try:
            val = request.form.get("money", 101, type=int)          # type: int
            # val = int(request.form["money"])                      # type: int
            name = request.form["f_name"]                           # type: str

            if val >= 0 or name:
                results_value = chain.search_value("gte", val)      # type: list
                results_name = chain.search_name(name)

                return render_template('search.html', data=results_value + results_name)
            else:
                print("Value is not a valid number")
        except Exception as e:
            print(f"Exception {e} occurred")
            tb = sys.exc_info()
            return e.with_traceback(tb)
    else:
        return render_template('search.html')


@app.route('/realtime')
def realtime():
    val = request.args.get('threshold', 101, type=int)              # type: int
    name = request.args.get('f_name', type=str)                     # type: str

    if val >= 0 or name:
        results_value = chain.search_value("gte", val)              # type: list
        results_name = chain.search_name(name)                      # type: list

        result = list()                                             # type: list

        if results_value:
            for item in results_value:
                temp = item.split('    ')                           # type: list
                result.append(temp[0])

        if results_name:
            for item in results_name:
                temp = item.split('    ')                           # type: list
                result.append(temp[0])

        return jsonify(result=result)
    else:
        return jsonify(result=[])


@app.route('/alert')
def alert_page():
    return render_template('alert.html')


@app.route('/ipswich')
def ipswich_page():
    return render_template('ipswich.html', name="Ruhma!")


@app.route('/test')
def test_page():
    val = request.args.get('threshold', 0, type=int)
    data = chain.search_value("gte", val)
    return render_template('test.html', data=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
