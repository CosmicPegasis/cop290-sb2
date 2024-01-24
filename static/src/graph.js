/* globals Chart */
"use strict";
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

async function get_past(symbol, offset, time_duration) {
  try {
    symbol = await fetch(
      `${backend}/request/query/${symbol}/${time_duration}/${offset}`,
      {
        mode: "cors",
        credentials: "same-origin",
      }
    );
    let res = await symbol.json();
    return res;
  } catch (err) {
    console.log(err);
  }
}
let chart = null;
let cur_symbols = [];
let offset = 0;

function get_selections(data) {
  let metric_checked = document.querySelector(
    "input[name=metric]:checked"
  ).value;
  if (metric_checked == "open") {
    return data.OPEN;
  } else if (metric_checked == "close") {
    return data.CLOSE;
  } else if (metric_checked == "high") {
    return data.HIGH;
  } else if (metric_checked == "low") {
    return data.LOW;
  } else if (metric_checked == "volume") {
    return data.VOLUME;
  }
}
function get_time_duration() {
  return document.querySelector("input[name=time]:checked").value;
}
// Create add and subtract buttons (later)
function plot_chart(graph_dates, graph_metrics) {
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
  const ctx = document.getElementById("myChart");
  if (chart) {
    chart.destroy();
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
function beautify_dates(dateObj) {
  let dates = [];
  for (let idx in dateObj) {
    let date = dateObj[idx].replace("00:00:00 GMT", "");
    dates.push(date);
  }
  return dates;
}
function redraw_stock_details(symbol, metrics) {
  let stockDetailDiv = document.getElementById("stock-details");
  let formDiv = document.getElementById("form-div");
  let compareDiv = document.getElementById("compare-div");
  stockDetailDiv.classList.add("col-4", "text-center");
  formDiv.classList.remove("col-6");
  formDiv.classList.add("col-4");
  compareDiv.classList.remove("col-6");
  compareDiv.classList.add("col-4");
  let delta = metrics[metrics.length - 1] - metrics[0];
  stockDetailDiv.innerHTML = `<h2 style="color: black; font-weight:bold">${symbol}`;
  if (delta >= 0) {
    //fontawesome.com/icons/triangle?f=classic&s=solid
    stockDetailDiv.innerHTML += `<div class="bg-success-subtle rounded-pill"><h3 class="text-success-emphasis"><i class="fa-solid fa-arrow-trend-up"></i>    ${delta.toFixed(
      2
    )}</h3></div>`;
  } else {
    stockDetailDiv.innerHTML += `<div class="bg-danger-subtle rounded-pill"><h3 class="text-danger-emphasis"><i class="fa-solid fa-arrow-trend-down"></i>   ${delta.toFixed(
      2
    )}</h3></div>`;
  }
}
async function redraw() {
  let graph_metrics = [];
  let graph_dates = [];
  for (let i = 0; i < cur_symbols.length; i++) {
    const symbol = cur_symbols[i];
    if (symbol == "" || !offset) continue;
    let time_duration = get_time_duration();
    const data = await get_past(symbol, offset, time_duration);
    let selections = get_selections(data);
    let metrics = [];
    let dateObj = data.DATE;
    let dates = beautify_dates(dateObj);
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
    if (i == 0) {
      redraw_stock_details(symbol, metrics);
    }
  }
  plot_chart(graph_dates, graph_metrics);
}
const autocolors = window["chartjs-plugin-autocolors"];
Chart.register(autocolors);
redraw();
let addBtn = document.getElementById("add-btn");
addBtn.addEventListener("click", (e) => {
  e.preventDefault();
  let formStruct = `<div class="row pb-1 pt-2"><div class="col-4"><input type="text" class="symbol-input form-control" placeholder="symbol"/></div></div>`;
  let compareDiv = document.getElementById("compare-div");
  compareDiv.insertAdjacentHTML("beforeend", formStruct);
});

let subBtn = document.getElementById("sub-btn");
subBtn.addEventListener("click", (e) => {
  e.preventDefault();
  let compareDiv = document.getElementById("compare-div");
  if (compareDiv.children.length > 1) {
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
      cur_symbols.push(sym_name);
    } else {
      cur_symbolsHTML[i].classList.add("is-invalid");
    }
  }
  offset = document.getElementById("year-input").value;
  if (cur_symbols.length > 0) {
    await redraw();
  }
});
