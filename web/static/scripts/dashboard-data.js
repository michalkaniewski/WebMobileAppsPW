let tableContent;
let form;
let addButton;

function deleteLabel(e) {
    fetch(`/label/${e.target.id}`, {method: 'DELETE'}).then(loadData());
}

function addLabel(form) {
    if (!form.checkValidity()) {
        return;
    }
    let fd = new FormData(form);
    fetch('/label', {
        method: 'POST',
        body: fd
    }).then(res => {
        if (res.status === 200) {
            loadData();
        }
    });
}

function loadData() {
    fetch('/label').then(res => {
        res.json().then(obj => fillTable(obj['labels']));
    })
    
}

function fillTable(labels) {
    while(tableContent.children.length > 0) {
        tableContent.deleteRow(0);
    }

    labels.forEach(label => {
        const row = tableContent.insertRow(-1);
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
    tableContent = document.getElementById("table-content");
    labelForm = document.getElementById("label-form");
    addButton = document.getElementById("add-button");
    addButton.onclick = () => addLabel(labelForm);
    loadData();
}