language = document.getElementById("assignmentLang").value;  
program = document.getElementById("assignmentProgram").value;

const assignmentForm = document.forms.assignmentForm;
assignmentForm.addEventListener("submit", checkAssignment)

const endpoint = "/api/check";
const url = `http://${window.location.hostname}:${window.location.port}${endpoint}`;
// "https://127.0.0.1:5000/api/check";

function checkAssignment(e) {
    const body = JSON.stringify(Object.fromEntries(new FormData(assignmentForm)))
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body
    })
    .then(resp => resp.json())
    .then(text =>{
        assignmentResult = document.getElementById("assignmentResult");
        assignmentResult.innerHTML = "";
        console.log(text);
        for (let i=1; i<text.length; i++) {
            console.log(text[i], i);
            elem = document.createElement("pre");
            elem.textContent = text[i];
            if (text[i].includes("ERROR") || text[i].includes("INCORRECT"))
                elem.style.color = "red";
            else
                elem.style.color = "green";
            assignmentResult.appendChild(elem);
        }
    })
    .catch(err => console.error(err));

}