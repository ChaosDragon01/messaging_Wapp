document.addEventListener("DOMContentLoaded", () => {
    const profileInput = document.getElementById("profile_pic");
    const preview = document.getElementById("profile_preview");

    profileInput.addEventListener("change", function () {
        const file = profileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = () => {
                preview.src = reader.result;
                preview.style.display = "block";
            };
            reader.readAsDataURL(file);
        }
    });
});
