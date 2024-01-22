const backend = "http://localhost:5000";

async function get_symbol_data() {
  try {
    symbol = await fetch(`${backend}/request/get_symbols/`, {
      mode: "cors",
      credentials: "same-origin",
    });
    res = await symbol.json();
    return res;
  } catch (err) {}
}

async function create_list() {
  data = await get_symbol_data();
  html = "";
  for (let symbol in data.AVG_PRICE) {
    html += `${symbol}<br>`;
  }
  return html;
}

async function get_past_years(symbol, years) {
  try {
    symbol = await fetch(`${backend}/request/query/${symbol}/${years}`, {
      mode: "cors",
      credentials: "same-origin",
    });
    res = await symbol.json();
    return res;
  } catch (err) {}
}
let symbolForm = document.getElementById("symbol-form");
let chart = null;
symbolForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  let symbol = document.getElementById("symbol-input").value;
  let years = document.getElementById("year-input").value;
  if (symbol != "" && years != "") {
    let data = await get_past_years(symbol, years);
    dates = [];
    close_prices = [];
    let dateObj = data.DATE;
    for (let idx in dateObj) {
      date = dateObj[idx].replace("00:00:00 GMT", "");
      dates.push(date);
    }
    for (let close_price in data.CLOSE) {
      close_prices.push(data.CLOSE[close_price]);
    }
    close_prices.reverse();
    dates.reverse();
    const ctx = document.getElementById("myChart");
    if (chart) {
      chart.destroy();
    }
    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: symbol,
            data: close_prices,
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }
});
