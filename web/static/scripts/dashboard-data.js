let table;

function deleteLabel(e) {
    // TODO: DELETE request
    console.log("wyrzucam " + e.target.id);
}

function loadData() {
    const labels = [
        {id: "1234", name: "w transporcie", receiver: "user1", size: "20kg", target: "WAW-1323"},
        {id: "2345", name: "w skrytce", receiver: "user2", size: "200g", target: "BIA-123"},
        {id: "3456", name: "anulowana", receiver: "user3", size: "2kg", target: "KRA-2343"}
    ];
    labels.forEach(label => {
        const row = table.insertRow(-1);
        for (key in label) {
            var cell = document.createElement('td');
            cell.appendChild(document.createTextNode(label[key]));
            row.appendChild(cell);
        }
        var deleteButton = document.createElement('button');
        deleteButton.id = label['id'];
        deleteButton.onclick = e => deleteLabel(e);
        deleteButton.innerText = "Usuń";
        var cell = document.createElement('td');
        cell.appendChild(deleteButton);
        row.appendChild(cell);
    });
}

window.onload = function () {
    table = document.getElementById("label-table");
    loadData();
}