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
let chart = null;
let cur_symbols = ["SBIN", "PAYTM"];
let years = 10;
let cur_selections = [];
let symbolForm = document.getElementById("symbol-form");

// Create add and subtract buttons (later)
async function redraw() {
  let graph_metrics = [];
  let graph_dates = [];
  for (let i = 0; i < cur_symbols.length; i++) {
    const symbol = cur_symbols[i];
    const data = await get_past_years(symbol, years);
    console.log("reached here");
    const selections = data.CLOSE; // add map for different selections
    metrics = [];
    dates = [];
    let dateObj = data.DATE;
    for (let idx in dateObj) {
      date = dateObj[idx].replace("00:00:00 GMT", "");
      dates.push(date);
    }
    for (let sel in selections) {
      metrics.push(selections[sel]);
    }
    metrics.reverse();
    dates.reverse();
    if (dates.length > graph_dates.length) {
      console.log(graph_dates);
      graph_dates = dates;
    }
    metric_dataset = { label: symbol, data: metrics };
    graph_metrics.push(metric_dataset);
  }
  const ctx = document.getElementById("myChart");
  if (chart) {
    chart.destroy();
  }
  let max_metric_size = 0;
  console.log(dates.length);
  for (let i = 0; i < graph_metrics.length; i++) {
    metric_size = graph_metrics[i].data.length;
    max_metric_size =
      metric_size > max_metric_size ? metric_size : max_metric_size;
  }
  for (let i = 0; i < graph_metrics.length; i++) {
    metric_size = graph_metrics[i].data.length;
    if (metric_size < max_metric_size) {
      let padding = Array(max_metric_size - metric_size).fill(0);
      padding = padding.concat(graph_metrics[i].data);
      graph_metrics[i].data = padding;
    }
  }
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: graph_dates,
      datasets: graph_metrics,
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          grid: { display: false },
        },
        x: {
          grid: { display: false },
        },
      },
      responsive: true,
      elements: {
        point: {
          pointStyle: false,
        },
      },
    },
  });
}
const autocolors = window["chartjs-plugin-autocolors"];
Chart.register(autocolors);
redraw();
// Use in-built colors
// symbolForm.addEventListener("submit", async (e) => {
//   e.preventDefault();
//   let symbol = document.getElementById("symbol-input").value;
//   let years = document.getElementById("year-input").value;
//   if (symbol != "" && years != "") {
//     let data = await get_past_years(symbol, years);
//     dates = [];
//     close_prices = [];
//     let dateObj = data.DATE;
//     for (let idx in dateObj) {
//       date = dateObj[idx].replace("00:00:00 GMT", "");
//       dates.push(date);
//     }
//     for (let close_price in data.CLOSE) {
//       close_prices.push(data.CLOSE[close_price]);
//     }
//     close_prices.reverse();
//     dates.reverse();
//     const ctx = document.getElementById("myChart");
//     if (chart) {
//       chart.destroy();
//     }
//     chart = new Chart(ctx, {
//       type: "line",
//       data: {
//         labels: dates,
//         datasets: [
//           {
//             label: symbol,
//             data: close_prices,
//             borderWidth: 1,
//           },
//         ],
//       },
//       options: {
//         scales: {
//           y: {
//             beginAtZero: true,
//             grid: { display: false },
//           },
//           x: {
//             grid: { display: false },
//           },
//         },
//         responsive: true,
//       },
//     });
//   }
// });
