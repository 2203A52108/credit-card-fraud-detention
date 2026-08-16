const form = document.getElementById("uploadForm");

const fileInput = document.getElementById("file");

const fileName = document.getElementById("fileName");


/* Show selected filename */

fileInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        fileName.textContent =
            this.files[0].name;

    } else {

        fileName.textContent =
            "Choose transaction CSV";

    }

});


/* Submit CSV */

form.addEventListener("submit", async function (event) {

    event.preventDefault();


    const file = fileInput.files[0];


    if (!file) {

        alert("Please select a CSV file.");

        return;

    }


    const formData = new FormData();

    formData.append("file", file);


    const resultElement =
        document.getElementById("result");

    const noteElement =
        document.getElementById("note");


    resultElement.textContent =
        "Analyzing...";

    noteElement.textContent =
        "XGBoost model is processing the transaction.";


    try {

        const response = await fetch(
            "/predict_csv",
            {
                method: "POST",
                body: formData
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Prediction failed."
            );

        }


        if (
            !data.results ||
            data.results.length === 0
        ) {

            throw new Error(
                "No prediction was returned."
            );

        }


        const result =
            data.results[0];


        const fraudProbability =
            Number(
                result.fraud_probability
            );


        const legitimateProbability =
            Number(
                result.legitimate_probability
            );


        /* Result */

        resultElement.textContent =
            result.prediction;


        document.getElementById("score")
            .textContent =
            fraudProbability + "%";


        document.getElementById("fraud")
            .textContent =
            fraudProbability + "%";


        document.getElementById("legit")
            .textContent =
            legitimateProbability + "%";


        document.getElementById("risk")
            .textContent =
            result.risk;


        /* Icon */

        const icon =
            document.getElementById("icon");


        if (
            result.prediction
                .toLowerCase()
                .includes("fraud")
        ) {

            icon.textContent = "!";

        } else {

            icon.textContent = "✓";

        }


        /* Ring */

        const degrees =
            fraudProbability * 3.6;


        const ringColor =
            result.prediction
                .toLowerCase()
                .includes("fraud")
                ? "#ff667a"
                : "#49d6a4";


        document.getElementById("ring")
            .style.background =
            `conic-gradient(
                ${ringColor} ${degrees}deg,
                #172a3e ${degrees}deg
            )`;


        /* Note */

        noteElement.textContent =
            `XGBoost analyzed ${data.count} transaction${
                data.count > 1 ? "s" : ""
            }.`;

    }


    catch (error) {

        resultElement.textContent =
            "Prediction Error";


        noteElement.textContent =
            error.message;


        console.error(error);

    }

});
