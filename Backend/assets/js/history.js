let currentSort = {};

function searchTable() {
  let input = document.getElementById("search").value.toLowerCase();
  let rows = document.querySelectorAll("#emailTable tbody tr");

  rows.forEach((row) => {
    let envoyeur = row.cells[0].textContent.toLowerCase();
    let objet = row.cells[2].textContent.toLowerCase();
    row.style.display =
      envoyeur.includes(input) || objet.includes(input) ? "" : "none";
  });
}

function sortTable(columnIndex) {
  let table = document.getElementById("emailTable");
  let rows = Array.from(table.rows).slice(1);
  let isNumeric = columnIndex === 1 || columnIndex === 3;
  let direction = currentSort[columnIndex] === "asc" ? "desc" : "asc";

  let sortedRows = rows.sort((a, b) => {
    let aText = a.cells[columnIndex].textContent.trim();
    let bText = b.cells[columnIndex].textContent.trim();

    if (isNumeric) {
      aText = columnIndex === 1 ? new Date(aText) : parseInt(aText);
      bText = columnIndex === 1 ? new Date(bText) : parseInt(bText);
    }

    return direction === "asc"
      ? aText > bText
        ? 1
        : -1
      : aText < bText
        ? 1
        : -1;
  });

  table.tBodies[0].append(...sortedRows);

  document.querySelectorAll(".sort-arrow").forEach((arrow) => {
    arrow.textContent = "↕️";
  });

  let arrow = document.querySelector(
    `.sort-arrow[data-column='${columnIndex}']`,
  );
  arrow.textContent = direction === "asc" ? "⬆️" : "⬇️";

  currentSort[columnIndex] = direction;
}
