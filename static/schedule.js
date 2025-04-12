document.addEventListener("DOMContentLoaded", () => {
    const cells = document.querySelectorAll(".schedule-cell");
    const modal = document.getElementById("edit-modal");
    const closeModal = document.getElementById("closeModal");
    const saveEvent = document.getElementById("saveEvent");
    const eventInput = document.getElementById("eventInput");
    const removeEvent = document.getElementById("removeEvent");
  
    let selectedCell = null;
  
    // Open modal on cell click
    cells.forEach(cell => {
      cell.addEventListener("click", () => {
        selectedCell = cell;
        eventInput.value = cell.textContent; // Prefill the input with existing event
        modal.style.display = "block"; // Display the modal
      });
    });
  
    // Close modal
    closeModal.addEventListener("click", () => {
      modal.style.display = "none"; // Hide the modal when close button is clicked
    });
  
    // Save event
    saveEvent.addEventListener("click", () => {
      const title = eventInput.value.trim();
  
      if (title === "") {
        alert("Please enter a title for the event.");
        return;
      }
  
      // Update the selected cell with the new event title
      selectedCell.textContent = title;
      selectedCell.style.backgroundColor = "#c2f0c2";
  
      // Close the modal after saving the event
      modal.style.display = "none";
      
    });
  
    // Remove event

    removeEvent.addEventListener("click", () => {
      selectedCell.textContent = ""; // Clear the cell content
      selectedCell.style.backgroundColor = ""; // Reset background color
      modal.style.display = "none"; // Hide the modal
    }
    );
    // Optional: Close the modal when clicking outside of it
    window.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.style.display = "none"; // Hide modal if clicked outside
      }
    });
  });