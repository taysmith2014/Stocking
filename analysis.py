from flask import (Blueprint, request, redirect, render_template, url_for)
from .Data_Management import Visualization
import json
import plotly
bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@bp.route('/output', methods=["GET", "POST"])
def output():
    if request.method == "POST":
        req = request.form

        global count
        global time_period, amount
        global graphJSON, beginningPieJSON, endPieJSON
        global sp500, tracers

        count = int(req.get("counter"))
        time_period = req.get("time_period")
        amount = req.get("amount")
        sp500 = req.get("sp500")
        tracers = req.get("tracers1")

        tickers = []
        weights = {}
        i = 1
        while i <= count:
            # create dictionary key for each asset as ticker symbol
            ticker_num = "ticker_" + str(i)
            key = req.get(ticker_num)
            key = key.split()[0]
            # create dictionary value for each asset as percentage
            weight_num = "weight_" + str(i)
            val = req.get(weight_num)
            val = float(val) / 100
            # add dictionary item to weights
            weights[key] = val
            # add ticker symbol to tickers array
            tickers.append(key)
            i += 1

        # Setting up the color map to have consistently colors across graphics
        color_index = 0
        colors = plotly.express.colors.qualitative.Plotly

        color_map = {}

        for ticker in tickers:
            color_map[ticker] = colors[color_index]
            color_index = color_index + 1
        color_map["Overall Portfolio"] = colors[color_index]
        if sp500 != None:
            weights["SPY"] = 1
            color_index = color_index + 1
            color_map["SPY"] = colors[color_index]
        # Get historical data for all tickers
        hist_data = Visualization.get_historical_data(tickers, time_period)
        # Get the performance of the entire portfolio
        performance = Visualization.calculate_performance(hist_data, weights, False)

        # Get the trace for the portfolio
        (performance_trace) = Visualization.get_traces(hist_data, performance, float(amount), weights, color_map)
        # Get the beginning pie and end pie for porfolio
        (beginning_pie, end_pie) = Visualization.get_pies(hist_data, float(amount), weights, color_map)
        data = [performance_trace]

        # Don't need to plot individual tickers if our portfolio is only comprised of one stock
        if len(tickers) != 1 and tracers != None:
            # Get the traces for each stock
            for individ_ticker in tickers:
                # Don't have to get historical data, take date and ticker data from hist_data
                individ_hist_data = hist_data[['date',individ_ticker]]
                # Get performance for this specific stock
                individ_performance = Visualization.calculate_performance(individ_hist_data, weights, True)
                # Get the trace for this specific stock
                individ_trace = Visualization.get_traces(individ_hist_data, individ_performance, float(amount) * weights[individ_ticker], weights, color_map)
                data.append(individ_trace)

        if sp500 != None:
            sp500_data = Visualization.get_historical_data(["SPY"],time_period)
            sp500_performance = Visualization.calculate_performance(sp500_data, weights, True)
            sp500_trace = Visualization.get_traces(sp500_data, sp500_performance, float(amount), weights, color_map)
            data.append(sp500_trace)

        # Turn data into JSON and send off
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        beginningPieJSON = json.dumps(beginning_pie, cls=plotly.utils.PlotlyJSONEncoder)
        endPieJSON = json.dumps(end_pie, cls=plotly.utils.PlotlyJSONEncoder)

        return redirect(request.url)

    return render_template('tool/index.html', scroll='analysis_output', time_period=time_period, amount=amount,
                           graphJSON=graphJSON, beginningPieJSON=beginningPieJSON, endPieJSON=endPieJSON)

