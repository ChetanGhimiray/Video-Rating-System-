(() => {
	const form = document.querySelector("[data-upload-form]");
	if (!form) return;

	const fileInput = form.querySelector('input[type="file"]');
	const fileName = document.getElementById("file-name");
	const progressPanel = document.getElementById("upload-progress");
	const progressBar = document.getElementById("upload-meter");
	const progressPercent = document.getElementById("upload-percent");
	const uploadStatus = document.getElementById("upload-status");
	const processingPanel = document.getElementById("processing-state");
	const processingStatus = document.getElementById("processing-status");
	const submitButton = form.querySelector('button[type="submit"]');

	fileInput?.addEventListener("change", () => {
		if (!fileName) return;
		const selected = fileInput.files?.[0];
		fileName.textContent = selected ? selected.name : "Choose a video file";
	});

	form.addEventListener("submit", (event) => {
		if (!window.XMLHttpRequest || !window.FormData) return;
		event.preventDefault();

		const selectedFile = fileInput?.files?.[0];
		const videoUrl = form.querySelector('input[name="video_url"]')?.value.trim();
		if (!selectedFile && !videoUrl) {
			form.reportValidity();
			return;
		}

		const xhr = new XMLHttpRequest();
		xhr.open("POST", form.action);
		submitButton.disabled = true;

		if (selectedFile) {
			progressPanel.hidden = false;
			progressBar.value = 0;
			uploadStatus.textContent = "Sending video to the review workspace.";
		} else {
			processingPanel.hidden = false;
			processingStatus.textContent = "Retrieving the video and preparing its review.";
		}

		xhr.upload.addEventListener("progress", (progressEvent) => {
			if (!progressEvent.lengthComputable) return;
			const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100);
			progressBar.value = percent;
			progressPercent.textContent = `${percent}%`;
		});

		xhr.upload.addEventListener("load", () => {
			if (!selectedFile) return;
			progressPanel.hidden = true;
			processingPanel.hidden = false;
			processingStatus.textContent = "Analyzing presentation delivery. This can take a little while.";
		});

		xhr.addEventListener("load", () => {
			if (xhr.getResponseHeader("content-type")?.includes("text/html")) {
				document.open();
				document.write(xhr.responseText);
				document.close();
				return;
			}
			showFailure("The review could not be completed. Please try again.");
		});

		xhr.addEventListener("error", () => {
			showFailure("The connection was interrupted. Check your network and try again.");
		});

		xhr.send(new FormData(form));
	});

	function showFailure(message) {
		progressPanel.hidden = true;
		processingPanel.hidden = true;
		submitButton.disabled = false;
		let error = form.querySelector("[data-upload-error]");
		if (!error) {
			error = document.createElement("div");
			error.className = "form-error";
			error.setAttribute("role", "alert");
			error.dataset.uploadError = "";
			form.before(error);
		}
		error.textContent = message;
	}
})();
