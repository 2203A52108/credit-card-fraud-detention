const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("file");
const fileName = document.getElementById("fileName");

const result = document.getElementById("result");
const icon = document.getElementById("icon");
const score = document.getElementById("score");
const fraud = document.getElementById("fraud");
const legit = document.getElementById("legit");
const risk = document.getElementById("risk");
const note = document.getElementById("note");

const probabilityFill =
    document.getElementById("probabilityFill");

const totalTransactions =
    document.getElementById("totalTransactions");

const fraudTransactions =
    document.getElementById("fraudTransactions");

const legitimateTransactions =
    document.getElementById("legitimateTransactions");

const averageProbability =
    document.getElementById("averageProbability");

const resultsTable =
    document.getElementById("resultsTable");


// ----------------------------------------------------
// FILE NAME
// ----------------------------------------------------

fileInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        fileName.textContent =
            this.files[0].name;

    } else {

        fileName.textContent =
            "No file selected";
    }
});


// ----------------------------------------------------
// FORM SUBMISSION
// ----------------------------------------------------

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    if (!fileInput.files.length) {

        alert("Please select a CSV file.");

        return;
    }


    const file = fileInput.files[0];

    const formData = new FormData();

    formData.append("file", file);


    // Loading state

    result.textContent = "Analyzing...";
    icon.textContent = "↻";

    score.textContent = "—";
    fraud.textContent = "—";
    legit.textContent = "—";
    risk.textContent = "Analyzing";

    note.textContent =
        "Processing your transaction data...";

    probabilityFill.style.width = "0%";


    try {

        const response = await fetch(
            "/predict_csv",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        // ------------------------------------------------
        // SERVER ERROR
        // ------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                "Prediction failed."
            );
        }


        if (!data.results ||
            data.results.length === 0) {

            throw new Error(
                "No prediction results returned."
            );
        }


        const results = data.results;


        // ------------------------------------------------
        // STATISTICS
        // ------------------------------------------------

        const total =
            results.length;


        const fraudCount =
            results.filter(
                item =>
                    item.prediction
                        .toLowerCase()
                        .includes("fraud")
            ).length;


        const legitimateCount =
            total - fraudCount;


        const probabilities =
            results.map(
                item =>
                    Number(
                        item.fraud_probability
                    )
            );


        const average =
            probabilities.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) / probabilities.length;


        totalTransactions.textContent =
            total;


        fraudTransactions.textContent =
            fraudCount;


        legitimateTransactions.textContent =
            legitimateCount;


        averageProbability.textContent =
            average.toFixed(2) + "%";


        // ------------------------------------------------
        // DISPLAY FIRST RESULT
        // ------------------------------------------------

        const first =
            results[0];


        const fraudProbability =
            Number(
                first.fraud_probability
            );


        const legitimateProbability =
            Number(
                first.legitimate_probability
            );


        score.textContent =
            fraudProbability.toFixed(2) + "%";


        fraud.textContent =
            fraudProbability.toFixed(2) + "%";


        legit.textContent =
            legitimateProbability.toFixed(2) + "%";


        risk.textContent =
            first.risk;


        result.textContent =
            first.prediction;


        probabilityFill.style.width =
            Math.min(
                Math.max(
                    fraudProbability,
                    0
                ),
                100
            ) + "%";


        // ------------------------------------------------
        // RESULT COLOR / ICON
        // ------------------------------------------------

        if (
            first.prediction
                .toLowerCase()
                .includes("fraud")
        ) {

            icon.textContent = "!";
            note.textContent =
                "This transaction has been classified as potentially fraudulent.";

            icon.style.color = "#ff647c";
            result.style.color = "#ff647c";
            risk.style.color = "#ff647c";

        } else {

            icon.textContent = "✓";
            note.textContent =
                "This transaction appears legitimate based on the model prediction.";

            icon.style.color = "#54dfaa";
            result.style.color = "#54dfaa";
            risk.style.color = "#54dfaa";
        }


        // ------------------------------------------------
        // RESULTS TABLE
        // ------------------------------------------------

        resultsTable.innerHTML = "";


        results.forEach(
            (item, index) => {

                const row =
                    document.createElement("tr");


                const fraudProbability =
                    Number(
                        item.fraud_probability
                    ).toFixed(2);


                const legitimateProbability =
                    Number(
                        item.legitimate_probability
                    ).toFixed(2);


                let riskClass =
                    "risk-low";


                if (
                    item.risk
                        .toLowerCase()
                        === "high"
                ) {

                    riskClass =
                        "risk-high";

                } else if (
                    item.risk
                        .toLowerCase()
                        === "medium"
                ) {

                    riskClass =
                        "risk-medium";
                }


                row.innerHTML = `

                    <td>
                        ${index + 1}
                    </td>

                    <td>
                        ${fraudProbability}%
                    </td>

                    <td>
                        ${legitimateProbability}%
                    </td>

                    <td>
                        ${item.prediction}
                    </td>

                    <td class="${riskClass}">
                        ${item.risk}
                    </td>

                `;


                resultsTable.appendChild(row);
            }
        );


    } catch (error) {

        console.error(error);


        result.textContent =
            "Prediction Error";


        icon.textContent =
            "!";


        score.textContent =
            "0%";


        fraud.textContent =
            "0%";


        legit.textContent =
            "100%";


        risk.textContent =
            "—";


        probabilityFill.style.width =
            "0%";


        note.textContent =
            error.message ||
            "Unable to analyze the CSV file.";


        resultsTable.innerHTML = `

            <tr>

                <td
                    colspan="5"
                    class="empty"
                >
                    ${error.message ||
                    "Prediction failed."}
                </td>

            </tr>

        `;
    }

});
