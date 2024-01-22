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
symbolForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  let symbol = document.getElementById("symbol-input").value;
  let years = document.getElementById("year-input").value;
  console.log("hello!");
  if (symbol != "" && years != "") {
    let data = await get_past_years(symbol, years);
    console.log(data);
  }
});
