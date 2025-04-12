let filePassed = false;

function confirmUpload(){
  const fileInput = document.getElementById("file-upload");
  const fileLabel = document.getElementById("file-upload-label");
  console.log(fileInput.files.length)

  if (fileInput.files.length > 0) {
    console.log("TRUE")
    fileLabel.textContent = fileInput.files[0].name;
    localStorage.setItem("filePassed", "true");
  } else {
    console.log("FALSE")
    localStorage.setItem("filePassed", "false");
    fileLabel.textContent = "Upload Degree Audit";
  }
}