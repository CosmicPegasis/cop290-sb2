const backend = "http://localhost:5000";

async function get_symbol_data() {
  try {
    let symbol = await fetch(`${backend}/request/get_symbols/`, {
      mode: "cors",
      credentials: "same-origin",
    });
    let res = await symbol.json();
    return res;
  } catch (err) {
    console.log(err);
  }
}
// Add symbol exists function

// async function create_list() {
//   let data = await get_symbol_data();
//   let html = "";
//   for (let symbol in data.AVG_PRICE) {
//     html += `${symbol}<br>`;
//   }
//   return html;
// }

async function get_past_years(symbol, years) {
  try {
    symbol = await fetch(`${backend}/request/query/${symbol}/${years}`, {
      mode: "cors",
      credentials: "same-origin",
    });
    let res = await symbol.json();
    return res;
  } catch (err) {
    console.log(err);
  }
}
let chart = null;
let cur_symbols = [];
let years = 10;

// Create add and subtract buttons (later)
async function redraw() {
  let graph_metrics = [];
  let graph_dates = [];

  let checked = document.querySelector("input[name=metric]:checked");

  for (let i = 0; i < cur_symbols.length; i++) {
    const symbol = cur_symbols[i];
    if (symbol == "" || !years) continue;
    const data = await get_past_years(symbol, years);
    if (!checked) return;
    let metric_option = checked.value;
    let selections = "";
    if (metric_option == "open") {
      selections = data.OPEN;
    } else if (metric_option == "close") {
      selections = data.CLOSE;
    } else if (metric_option == "high") {
      selections = data.HIGH;
    } else if (metric_option == "low") {
      selections = data.LOW;
    } else if (metric_option == "volume") {
      selections = data.VOLUME;
    }
    let metrics = [];
    let dates = [];
    let dateObj = data.DATE;
    for (let idx in dateObj) {
      let date = dateObj[idx].replace("00:00:00 GMT", "");
      dates.push(date);
    }
    for (let sel in selections) {
      metrics.push(selections[sel]);
    }
    metrics.reverse();
    dates.reverse();
    if (dates.length > graph_dates.length) {
      graph_dates = dates;
    }
    let metric_dataset = { label: symbol, data: metrics };
    graph_metrics.push(metric_dataset);
  }
  const ctx = document.getElementById("myChart");
  if (chart) {
    chart.destroy();
  }
  let max_metric_size = 0;
  for (let i = 0; i < graph_metrics.length; i++) {
    let metric_size = graph_metrics[i].data.length;
    max_metric_size =
      metric_size > max_metric_size ? metric_size : max_metric_size;
  }
  for (let i = 0; i < graph_metrics.length; i++) {
    let metric_size = graph_metrics[i].data.length;
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
let addBtn = document.getElementById("add-btn");
addBtn.addEventListener("click", (e) => {
  e.preventDefault();
  let formStruct = `<div class="pb-1 pt-2"><input type="text" class="symbol-input form-control" placeholder="symbol"/></div>`;
  let compareDiv = document.getElementById("compare-div");
  compareDiv.insertAdjacentHTML("beforeend", formStruct);
});

let subBtn = document.getElementById("sub-btn");
subBtn.addEventListener("click", (e) => {
  e.preventDefault();
  let compareDiv = document.getElementById("compare-div");
  if (compareDiv.children.length > 2) {
    compareDiv.removeChild(compareDiv.lastChild);
  }
});

let symbolForm = document.getElementById("symbol-form");
symbolForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  let cur_symbolsHTML = document.getElementsByClassName("symbol-input");
  cur_symbols = [];
  let all_symbol_data = await get_symbol_data();
  for (let i = 0; i < cur_symbolsHTML.length; i++) {
    let sym_name = cur_symbolsHTML[i].value;
    if (
      Object.prototype.hasOwnProperty.call(all_symbol_data.AVG_PRICE, sym_name)
    ) {
      cur_symbolsHTML[i].classList.remove("is-invalid");
      console.log(sym_name);
      cur_symbols.push(sym_name);
    } else {
      cur_symbolsHTML[i].classList.add("is-invalid");
    }
  }
  years = document.getElementById("year-input").value;
  if (cur_symbols.length > 0) {
    await redraw();
  }
});
