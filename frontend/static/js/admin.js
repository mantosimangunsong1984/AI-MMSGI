const uploadButton =
    document.getElementById("upload-btn");

const fileInput =
    document.getElementById("document");

const result =
    document.getElementById("result");


uploadButton.onclick = async function () {

    if (fileInput.files.length === 0) {

        alert("Pilih file.");

        return;

    }

    const formData = new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    result.innerHTML =
        "Uploading...";

    try {

        const response =
            await fetch(
                "/api/documents/upload",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail
            );

        }

        result.innerHTML = `
            <h3>Upload Berhasil</h3>

            <p>
                File :
                ${data.filename}
            </p>

            <p>
                Chunk :
                ${data.chunks}
            </p>

            <p>
                Status :
                ${data.status}
            </p>
        `;

    }

    catch (err) {

        result.innerHTML =
            err.message;

    }

};