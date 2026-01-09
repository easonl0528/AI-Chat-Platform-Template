async function requestJSON(url, options = {}) {
  const resp = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(payload.error || "请求失败");
  }
  return payload;
}

function renderResult(target, data) {
  target.textContent = JSON.stringify(data, null, 2);
}

async function handleOptimize() {
  const promptInput = document.getElementById("prompt-input");
  const resultBox = document.getElementById("optimize-result");
  resultBox.textContent = "执行中...";
  try {
    const data = await requestJSON("/api/optimize", {
      method: "POST",
      body: JSON.stringify({ prompt: promptInput.value || promptInput.placeholder }),
    });
    renderResult(resultBox, data);
  } catch (err) {
    resultBox.textContent = err.message;
  }
}

async function refreshPrompts() {
  const listBox = document.getElementById("prompt-list");
  listBox.textContent = "加载中...";
  try {
    const data = await requestJSON("/api/prompts");
    if (!data.length) {
      listBox.textContent = "暂无数据";
      return;
    }
    listBox.innerHTML = data
      .map(
        (p) =>
          `<div><strong>${p.title}</strong> · ${p.category} · ${p.tags?.join("/") || ""}<br/>ID: ${p.id}<br/>${p.content}</div>`
      )
      .join("<hr/>");
  } catch (err) {
    listBox.textContent = err.message;
  }
}

async function addPrompt() {
  const title = document.getElementById("prompt-title").value;
  const category = document.getElementById("prompt-category").value;
  const content = document.getElementById("prompt-content").value;
  const tags = document
    .getElementById("prompt-tags")
    .value.split(/\s+/)
    .filter(Boolean);
  const listBox = document.getElementById("prompt-list");
  listBox.textContent = "提交中...";
  try {
    await requestJSON("/api/prompts", {
      method: "POST",
      body: JSON.stringify({ title, category, content, tags }),
    });
    await refreshPrompts();
  } catch (err) {
    listBox.textContent = err.message;
  }
}

async function refreshPublish() {
  const listBox = document.getElementById("publish-list");
  listBox.textContent = "加载中...";
  try {
    const data = await requestJSON("/api/publish");
    if (!data.length) {
      listBox.textContent = "暂无任务";
      return;
    }
    listBox.innerHTML = data
      .map((task) => `<div><strong>${task.id}</strong> · ${task.channel} · ${task.status}<br/>prompt: ${task.prompt_id}<br/>${task.notes}</div>`)
      .join("<hr/>");
  } catch (err) {
    listBox.textContent = err.message;
  }
}

async function queueTask() {
  const promptId = document.getElementById("task-prompt-id").value;
  const channel = document.getElementById("task-channel").value;
  const notes = document.getElementById("task-notes").value;
  const listBox = document.getElementById("publish-list");
  listBox.textContent = "提交中...";
  try {
    await requestJSON("/api/publish", {
      method: "POST",
      body: JSON.stringify({ prompt_id: promptId, channel, notes }),
    });
    await refreshPublish();
    await refreshStats();
  } catch (err) {
    listBox.textContent = err.message;
  }
}

async function updateTask() {
  const id = document.getElementById("update-task-id").value;
  const status = document.getElementById("update-task-status").value;
  const listBox = document.getElementById("publish-list");
  listBox.textContent = "更新中...";
  try {
    await requestJSON(`/api/publish/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    await refreshPublish();
    await refreshStats();
  } catch (err) {
    listBox.textContent = err.message;
  }
}

async function refreshStats() {
  const box = document.getElementById("publish-stats");
  box.textContent = "统计中...";
  try {
    const data = await requestJSON("/api/publish/stats");
    renderResult(box, data);
  } catch (err) {
    box.textContent = err.message;
  }
}

function bindEvents() {
  document.getElementById("optimize-btn").addEventListener("click", handleOptimize);
  document.getElementById("add-prompt-btn").addEventListener("click", addPrompt);
  document.getElementById("queue-task-btn").addEventListener("click", queueTask);
  document.getElementById("update-task-btn").addEventListener("click", updateTask);
  document.getElementById("refresh-stats-btn").addEventListener("click", refreshStats);
}

bindEvents();
refreshPrompts();
refreshPublish();
refreshStats();
handleOptimize();
