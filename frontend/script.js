// 1. Highlight Active Sidebar Link
document.querySelectorAll(".nav-links a").forEach(link => {
    link.addEventListener("click", () => {
      document.querySelectorAll(".nav-links a").forEach(l => l.classList.remove("active"));
      link.classList.add("active");
    });
  });
  
  // 2. File Upload with Validation
const uploadBtn = document.querySelector(".upload-btn");
const fileInput = document.getElementById("fileInput");
const uploadBox = document.querySelector(".upload-box");

// Click button => open file dialog
uploadBtn.addEventListener("click", () => {
  fileInput.click();
});

// File selected => validate
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  const validTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];
  const maxSize = 10 * 1024 * 1024; // 10 MB

  if (!validTypes.includes(file.type)) {
    showToast("❌ Invalid file type. Please upload a PDF, DOC, or DOCX file.");
    return;
  }

  if (file.size > maxSize) {
    showToast("❌ File is too large. Max size is 10 MB.");
    return;
  }

  // Real upload via backend
  const formData = new FormData();
  formData.append("file", file);

  fetch("http://127.0.0.1:5000/upload", {
    method: "POST",
    body: formData,
  })
  .then(async response => {
    const text = await response.text();
    console.log("Raw response:", text);
    try {
      const data = JSON.parse(text);
      if (data.message) {
        showToast("✅ " + data.message);
      } else if (data.error) {
        showToast("❌ " + data.error);
      } else {
        showToast("❌ Unknown server response.");
      }
    } catch (err) {
      console.error("Failed to parse JSON:", err);
      showToast("❌ Server did not return valid JSON.");
    }
  })
  
    
    .catch(err => {
      console.error("Upload error:", err);
      showToast("❌ Upload failed due to network or server issue.");
    });
});

// Optional: drag and drop support (uses the same validation)
uploadBox.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadBox.style.borderColor = "#3b82f6";
});

uploadBox.addEventListener("dragleave", () => {
  uploadBox.style.borderColor = "#ccc";
});

uploadBox.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadBox.style.borderColor = "#ccc";

  const file = e.dataTransfer.files[0];
  if (!file) return;

  const validTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];
  const maxSize = 10 * 1024 * 1024; // 10 MB

  if (!validTypes.includes(file.type)) {
    showToast("❌ Invalid file type. Please upload a PDF, DOC, or DOCX file.");
    return;
  }

  if (file.size > maxSize) {
    showToast("❌ File is too large. Max size is 10 MB.");
    return;
  }

  showToast(`✅ File "${file.name}" uploaded successfully! (simulated)`);
});

  
  // 3. View All Button (Toggle table rows)
  const viewAllBtn = document.querySelector(".view-all");
  let expanded = false;
  
  viewAllBtn.addEventListener("click", () => {
    const table = document.querySelector("table tbody");
    if (!expanded) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><span class="tag">Sample</span> ContractX.pdf</td>
        <td><span class="status ready">Ready</span></td>
        <td>MSA</td>
        <td>SpeedLegal MSA Market V3.0</td>
        <td><span class="exposure orange">62%</span></td>
        <td>Jan 3, 2024</td>
      `;
      table.appendChild(row);
      viewAllBtn.textContent = "View Less ⌃";
      expanded = true;
    } else {
      table.lastChild.remove();
      viewAllBtn.textContent = "View All ⌄";
      expanded = false;
    }
  });
  
  // 4. Toast Message
  function showToast(message) {
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.className = "toast";
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 2500);
  }
  