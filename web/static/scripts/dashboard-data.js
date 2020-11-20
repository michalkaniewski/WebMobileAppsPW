let table;

function deleteLabel(e) {
    // TODO: DELETE request
    console.log("wyrzucam " + e.target.id);
}

function loadData() {
    let labels = [];
    fetch('/label').then(res => {
        res.json().then(obj => fillTable(obj['labels']));
        
    })
    
}

function fillTable(labels) {
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