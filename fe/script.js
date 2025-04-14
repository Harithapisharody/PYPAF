// script.js
document.getElementById("generateForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let studentInput = document.getElementById("studentInput").value.trim();
    
    // const PseudoCodeHeading = document.getElementById("PseudoCodeHeading");
    // const generatedPseudocodeElement = document.getElementById("generatedPseudocode");

    const generatedAlgorithmElement = document.getElementById("generatedAlgorithm");
    const generatedAlgorithmHeading = document.getElementById("generatedAlgorithmHeading");

    const generatedFlowchart = document.getElementById("generatedFlowchart");
    const flowchartImage = document.getElementById("flowchartImage");
    const generatedFlowchartHeading = document.getElementById("generatedFlowchartHeading");

    const generatedCodeHeading = document.getElementById("generatedCodeHeading");
    const editableCodeElement = document.getElementById("editableCode");
    const copyButton = document.getElementById("copyButton");
    const runButton = document.getElementById("runButton");

    // Reset visibility and content
    // PseudoCodeHeading.style.display = 'none';
    // generatedPseudocodeElement.style.display = 'none';
    // generatedPseudocodeElement.value = '';

    generatedAlgorithmElement.style.display = 'none';
    generatedAlgorithmElement.value = '';

    generatedFlowchart.style.display = 'none';
    flowchartImage.src = '';  // Reset flowchart image
    generatedFlowchartHeading.style.display = 'none';  // Hide flowchart heading initially
    generatedAlgorithmHeading.style.display = 'none';
    
    generatedCodeHeading.style.display = 'none';
    editableCodeElement.style.display = 'none';
    editableCodeElement.value = '';
    copyButton.style.display = 'none';
    runButton.style.display = 'none';

    if (studentInput) {
        try {
            const data = await postData('/generate/student', { logic: studentInput });

            // if (data.pseudocode) {
            //     // Display generated code
            //     generatedPseudocodeElement.textContent = data.pseudocode;
            //     PseudoCodeHeading.style.display = 'block';
            //     generatedPseudocodeElement.style.display = 'block';
                

                // Display generated algorithm
                if (data.algorithm) {
                    generatedAlgorithmElement.textContent = data.algorithm;
                    generatedAlgorithmHeading.style.display = 'block';
                    generatedAlgorithmElement.style.display = 'block';
                

                // Display generated flowchart
                if (data.flowchart) {
                    flowchartImage.src = `${baseURL}/${data.flowchart}.png?t=${new Date().getTime()}`;
                    generatedFlowchart.style.display = 'block';
                    generatedFlowchartHeading.style.display = 'block';
                }

                if (data.code_generation) {
                    editableCodeElement.value = data.code_generation;
                    generatedCodeHeading.style.display = 'block';
                    editableCodeElement.style.display = 'block';
                    copyButton.style.display = 'inline-block';
                    runButton.style.display = 'inline-block';
                }
            } else if (data.error) {
                editableCodeElement.value = `Error: ${data.error}`;
                generatedCodeHeading.style.display = 'block';
                editableCodeElement.style.display = 'block';
            }
        } catch (error) {
            editableCodeElement.value = 'Error generating code.';
            editableCodeElement.style.display = 'block';
            generatedCodeHeading.style.display = 'block';
        }
    }
});

// Copy code to clipboard
document.getElementById("copyButton").addEventListener("click", function() {
    const code = document.getElementById("editableCode").value;
    navigator.clipboard.writeText(code).then(function() {
        alert('Code copied to clipboard!');
    }, function(err) {
        console.error('Error copying code: ', err);
    });
});

// Run edited code
document.getElementById("runButton").addEventListener("click", async function() {
    const code = document.getElementById("editableCode").value;

    try {
        const data = await postData('/run', { code: code });
        if (data.output) {
            alert('Output: ' + data.output);
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error running code.');
    }
});



// Handle navigation between sections
// Handle Student button click
document.getElementById("studentBtn").addEventListener("click", function () {
    document.getElementById("frontPage").style.display = "none";
    document.getElementById("teacherSection").style.display = "none"; // Hide Teacher Section
    document.getElementById("studentSection").style.display = "block";
    document.getElementById("backArrow").style.display = "block";
});

// Handle Teacher button click
document.getElementById("teacherBtn").addEventListener("click", function () {
    document.getElementById("frontPage").style.display = "none";
    document.getElementById("studentSection").style.display = "none"; // Hide Student Section
    document.getElementById("teacherSection").style.display = "block";
    document.getElementById("backArrow").style.display = "block";
});

// Universal back arrow function
document.getElementById("backArrow").addEventListener("click", function () {
    document.getElementById("studentSection").style.display = "none";
    document.getElementById("teacherSection").style.display = "none";
    document.getElementById("frontPage").style.display = "flex";
    document.getElementById("backArrow").style.display = "none";
});

document.getElementById("teacherGenerateBtn").addEventListener("click", async function () {
    let teacherInput = document.getElementById("teacherInput").value.trim();

   

    
    const teacher_generatedCodeHeading = document.getElementById("teacher_generatedCodeHeading");
    const teacher_editableCodeElement = document.getElementById("teacher_editableCode");
    const saveButton = document.getElementById("saveButton");
    const uploadFolderButton = document.getElementById("uploadFolderButton");
    const teacher_EvaluateBtn = document.getElementById("teacher_EvaluateBtn");
    const teacher_runButton = document.getElementById("teacher_runButton");

    

    teacher_generatedCodeHeading.style.display = 'none';
    teacher_editableCodeElement.style.display = 'none';
    teacher_editableCodeElement.value = '';
    saveButton.style.display = 'none';
    uploadFolderButton.style.display = 'none';
    teacher_EvaluateBtn.style.display = 'none';
    teacher_runButton.style.display = 'none';

    if (teacherInput) {
        try {
            const data = await postData('/generate/teacher', { logic: teacherInput });
            console.log(data);
            if (data.code_generation) {
                teacher_editableCodeElement.value = data.code_generation;
                teacher_generatedCodeHeading.style.display = 'block';
                teacher_editableCodeElement.style.display = 'block';
                saveButton.style.display = 'inline-block';
                uploadFolderButton.style.display = 'inline-block';
                teacher_EvaluateBtn.style.display = 'inline-block';
                teacher_runButton.style.display = 'inline-block';
            }
         else if (data.error) {
            teacher_editableCodeElement.value = `Error: ${data.error}`;
            teacher_generatedCodeHeading.style.display = 'block';
            teacher_editableCodeElement.style.display = 'block';
        }
        } catch (error) {
            teacher_editableCodeElement.value = 'Error generating code.';
            teacher_editableCodeElement.style.display = 'block';
            teacher_generatedCodeHeading.style.display = 'block';
        }
    }
});


// Run edited code
document.getElementById("teacher_runButton").addEventListener("click", async function() {
    const code = document.getElementById("teacher_editableCode").value;

    try {
        const data = await postData('/run', { code: code });
        if (data.output) {
            alert('Output: ' + data.output);
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error running code.');
    }
});


// Save the generated code when the save button is clicked
document.getElementById("saveButton").addEventListener("click", async function() {
    const teacherGeneratedCode = document.getElementById("teacher_editableCode").value;

    // Only proceed if the generated code is not empty
    if (teacherGeneratedCode.trim() !== '') {
        try {
            const dataToSend = { code: teacherGeneratedCode };
            console.log("Sending data to backend:", dataToSend);  // Log data before sending
            
            // Sending the code to the backend to store it in reference.py
            const data = await postData('/save/generated_code', dataToSend);

            if (data.message) {
                alert('Code saved successfully!');
            } else if (data.error) {
                alert('Error saving code: ' + data.error);
            }
        } catch (error) {
            console.error('Error saving code:', error);
            alert('Error saving code.');
        }
    } else {
        alert('No code to save!');
    }
});

// Show the folder input when the "Upload Folder" button is clicked
// Handle Folder Upload Button Click to Trigger Folder Selection
document.getElementById("uploadFolderButton").addEventListener("click", function () {
    document.getElementById("folderInput").click();  // Trigger folder input click
});

// Handle Folder Selection (Multiple Files)
document.getElementById("folderInput").addEventListener("change", async function (event) {
    const formData = new FormData();
    const files = event.target.files; // Get all files inside the selected folder

    // Append all files to formData
    for (let i = 0; i < files.length; i++) {
        formData.append('folder', files[i]);
    }

    // Send the FormData via fetch to the backend
    fetch('http://127.0.0.1:5000/upload/folder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display backend message in an alert box
        alert(data.message || data.text);
    })
    .catch(error => {
        alert("Error uploading folder: " + error);
    });
});
// Evaluate button logic
document.getElementById("teacher_EvaluateBtn").addEventListener("click", async function () {
    const downloadReportBtn = document.getElementById("downloadReportBtn");
    const resultsTableHeading = document.getElementById("resultsTableHeading");
    const resultsTable = document.getElementById("resultsTable");
    const resultsTableHead = document.getElementById("resultsTableHead");
    const resultsTableBody = document.getElementById("resultsTableBody");

    try {
        const response = await getData('/evaluate');
        console.log("Response status:", response.status);
        console.log("Response headers:", response.headers.get("Content-Type"));

        const data = await response.json();
        console.log("Received data:", data);

        if (data.status === "success") {
            alert("Evaluation completed successfully!\n\n");
            downloadReportBtn.style.display = "inline-block";

            if (data.csv_data && data.csv_data.length > 0) {
                console.log("CSV data exists, rendering table:", data.csv_data);
                resultsTableHeading.style.display = "block";
                resultsTable.style.display = "table";
                resultsTableHead.innerHTML = "";
                resultsTableBody.innerHTML = "";

                const headers = Object.keys(data.csv_data[0]);
                const headerRow = document.createElement("tr");
                headers.forEach(header => {
                    const th = document.createElement("th");
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                resultsTableHead.appendChild(headerRow);

                data.csv_data.forEach(row => {
                    const tr = document.createElement("tr");
                    headers.forEach(header => {
                        const td = document.createElement("td");
                        td.textContent = row[header] ?? "";
                        tr.appendChild(td);
                    });
                    resultsTableBody.appendChild(tr);
                });
            } else {
                console.log("No CSV data received or empty:", data.csv_data);
                resultsTableHeading.style.display = "none";
                resultsTable.style.display = "none";
            }
        } else {
            alert(`Evaluation failed!\nError: ${data.text}\nDetails: ${data.error}\nOutput: ${data.stdout}`);
            resultsTableHeading.style.display = "none";
            resultsTable.style.display = "none";
        }
    } catch (error) {
        alert("Error connecting to the server: " + error.message);
        console.error("Full error:", error);
        resultsTableHeading.style.display = "none";
        resultsTable.style.display = "none";
    }
});
// Download Report button logic
document.getElementById("downloadReportBtn").addEventListener("click", async function () {
    try {
        const response = await getData('/download_report');
        if (!response.ok) {
            throw new Error('Failed to download report');
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "evaluation_results.csv";
        link.click();
    } catch (error) {
        alert("Error downloading report: " + error.message);
    }
});