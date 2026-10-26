
console.log("JavaScript is working!");

const API_URL = "http://127.0.0.1:5000/api/students";

const tableBody = document.getElementById("studentsTable");
const studentCount = document.getElementById("studentCount");
const searchInput = document.getElementById("searchInput");
const statusMessage = document.getElementById("statusMessage");
const refreshBtn = document.getElementById("refreshBtn");

const studentModal = document.getElementById("studentModal");
const newStudentBtn = document.getElementById("newStudentBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const studentForm = document.getElementById("studentForm");
const formTitle = document.getElementById("formTitle");
const formMessage = document.getElementById("formMessage");
const studentIdInput = document.getElementById("studentId");
const saveButton = document.getElementById("saveStudentBtn");

let students = [];

async function loadStudents() {
    statusMessage.textContent = "Loading data...";
    refreshBtn.disabled = true;

    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error("Invalid data format");
        }

        students = data;
        renderStudents();
    } catch (error) {
        console.error("Student API error:", error);
        statusMessage.textContent =
            "Failed to load students. Check Flask and MySQL.";
    } finally {
        refreshBtn.disabled = false;
    }
}

function renderStudents() {
    const query = searchInput.value.trim().toLowerCase();

    const filteredStudents = students.filter(student => {
        return [
            student.name,
            student.email,
            student.phone
        ].some(value => String(value ?? "").toLowerCase().includes(query));
    });

    studentCount.textContent = students.length;
    tableBody.replaceChildren();

    if (filteredStudents.length === 0) {
        statusMessage.textContent = students.length === 0
            ? "No student data to display."
            : "No student found matching the search.";
        return;
    }

    statusMessage.textContent =
        `Number of results: ${filteredStudents.length}`;

    filteredStudents.forEach(student => {
        const row = document.createElement("tr");

        [
            student.id,
            student.name,
            student.email,
            student.phone,
            student.gender
        ].forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value ?? "—";
            row.appendChild(cell);
        });

        const actionsCell = document.createElement("td");

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.className = "btn btn-secondary";
        editButton.addEventListener("click", () => editStudent(student));

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.className = "btn btn-primary";
        deleteButton.style.marginInlineStart = "8px";
        deleteButton.addEventListener("click", () => deleteStudent(student.id));

        actionsCell.append(editButton, deleteButton);
        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    });
}

function openNewStudentModal() {
    studentForm.reset();
    studentIdInput.value = "";
    formTitle.textContent = "New Student";
    saveButton.textContent = "Add Student";
    formMessage.textContent = "";
    studentModal.hidden = false;
}

function editStudent(student) {
    studentForm.reset();
    studentIdInput.value = student.id;
    document.getElementById("studentName").value = student.name ?? "";
    document.getElementById("studentEmail").value = student.email ?? "";
    document.getElementById("studentPhone").value = student.phone ?? "";
    document.getElementById("studentGender").value = student.gender ?? "";

    formTitle.textContent = "Edit Student";
    saveButton.textContent = "Save Changes";
    formMessage.textContent = "";
    studentModal.hidden = false;
}

async function deleteStudent(id) {
    if (!confirm("Are you sure you want to delete this student?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to delete student");
        }

        await loadStudents();
    } catch (error) {
        console.error("Delete student error:", error);
        alert(error.message);
    }
}

newStudentBtn.addEventListener("click", openNewStudentModal);

closeModalBtn.addEventListener("click", () => {
    studentModal.hidden = true;
});

studentModal.addEventListener("click", event => {
    if (event.target === studentModal) {
        studentModal.hidden = true;
    }
});

searchInput.addEventListener("input", renderStudents);
refreshBtn.addEventListener("click", loadStudents);

studentForm.addEventListener("submit", async event => {
    event.preventDefault();

    const id = studentIdInput.value;

    const student = {
        name: document.getElementById("studentName").value.trim(),
        email: document.getElementById("studentEmail").value.trim(),
        phone: document.getElementById("studentPhone").value.trim(),
        gender: document.getElementById("studentGender").value
    };

    saveButton.disabled = true;
    formMessage.textContent = "Saving...";

    try {
        const response = await fetch(
            id ? `${API_URL}/${id}` : API_URL,
            {
                method: id ? "PUT" : "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(student)
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to save student");
        }

        await loadStudents();
        studentModal.hidden = true;
        studentForm.reset();
        studentIdInput.value = "";
    } catch (error) {
        console.error("Save student error:", error);
        formMessage.textContent = error.message;
    } finally {
        saveButton.disabled = false;
    }
});

loadStudents();
