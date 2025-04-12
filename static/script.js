document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const imageList = document.getElementById("image-list");
  const downloadAll = document.getElementById("download-all");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    loading.style.display = "block";
    result.style.display = "none";
    imageList.innerHTML = "";

    fetch("/convert", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        loading.style.display = "none";

        if (data.success) {
          result.style.display = "block";

          // 이미지 리스트 렌더링
          data.images.forEach((imgUrl) => {
            const img = document.createElement("img");
            img.src = imgUrl;
            img.alt = "변환된 이미지";
            imageList.appendChild(img);
          });

          // 전체 다운로드 링크 지정
          downloadAll.href = data.zip_url;
          downloadAll.setAttribute("download", "converted_images.zip");
        } else {
          alert("변환 중 오류가 발생했습니다.");
        }
      })
      .catch((error) => {
        loading.style.display = "none";
        alert("서버와 통신 중 문제가 발생했습니다.");
        console.error("Error:", error);
      });
  });
});
