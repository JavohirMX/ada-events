document.addEventListener("DOMContentLoaded", () => {
  const authForms = document.querySelectorAll("form.auth-form");
  if (!authForms.length) {
    return;
  }

  const HINT_SIMILAR = "Your password can’t be too similar to your other personal information.";
  const HINT_LENGTH = "Your password must contain at least 8 characters.";
  const HINT_COMMON = "Your password can’t be a commonly used password.";
  const HINT_NUMERIC = "Your password can’t be entirely numeric.";
  const PASSWORD_RULE_MARKERS = [
    "too similar to your other personal information",
    "at least 8 characters",
    "commonly used password",
    "entirely numeric",
  ];
  const COMMON_PASSWORDS = new Set([
    "password",
    "password123",
    "12345678",
    "123456789",
    "qwerty123",
    "abc12345",
    "letmein",
    "welcome123",
  ]);

  const applyInputBehavior = (input) => {
    const name = (input.getAttribute("name") || "").toLowerCase();
    const id = (input.getAttribute("id") || "").toLowerCase();

    input.setAttribute("autocapitalize", "none");
    input.setAttribute("autocorrect", "off");
    input.setAttribute("spellcheck", "false");

    if (name.includes("email") || id.includes("email")) {
      input.setAttribute("autocomplete", "email");
      input.setAttribute("inputmode", "email");
      input.setAttribute("enterkeyhint", "next");
      return;
    }

    if (name === "login" || id.includes("login") || name.includes("username")) {
      input.setAttribute("autocomplete", "username");
      input.setAttribute("enterkeyhint", "next");
      return;
    }

    if (name.includes("password") || input.type === "password") {
      if (name.includes("old") || name.includes("current")) {
        input.setAttribute("autocomplete", "current-password");
      } else {
        input.setAttribute("autocomplete", "new-password");
      }
      input.setAttribute("enterkeyhint", "done");
    }
  };

  const styleHintNode = (node) => {
    node.classList.add(
      "text-sm",
      "leading-6",
      "text-gray-600",
      "dark:text-gray-300",
      "mt-2",
      "space-y-1",
      "list-disc",
      "pl-5"
    );
  };

  const getPasswordIssues = (passwordValue, form) => {
    const issues = [];
    const normalizedPassword = passwordValue.toLowerCase();

    if (passwordValue.length < 8) {
      issues.push(HINT_LENGTH);
    }

    if (/^\d+$/.test(passwordValue)) {
      issues.push(HINT_NUMERIC);
    }

    if (COMMON_PASSWORDS.has(normalizedPassword)) {
      issues.push(HINT_COMMON);
    }

    const personalInfoSelectors = [
      'input[name="email"]',
      'input[name="login"]',
      'input[name="username"]',
      'input[name="email_or_username"]',
    ];

    const candidateParts = [];
    personalInfoSelectors.forEach((selector) => {
      const field = form.querySelector(selector);
      if (!field || !field.value) {
        return;
      }

      const value = field.value.trim().toLowerCase();
      if (!value) {
        return;
      }

      candidateParts.push(value);

      if (value.includes("@")) {
        const localPart = value.split("@")[0];
        if (localPart) {
          candidateParts.push(localPart);
        }
      }
    });

    const hasSimilarity = candidateParts.some((part) => {
      const cleaned = part.replace(/[^a-z0-9]/g, "");
      return cleaned.length >= 3 && normalizedPassword.includes(cleaned);
    });

    if (hasSimilarity) {
      issues.push(HINT_SIMILAR);
    }

    return issues;
  };

  const ensureIssueList = (passwordInput) => {
    const existing = passwordInput.parentElement?.querySelector(".password-issues");
    if (existing) {
      styleHintNode(existing);
      return existing;
    }

    const issueList = document.createElement("ul");
    issueList.className = "password-issues hidden";
    issueList.setAttribute("aria-live", "polite");
    styleHintNode(issueList);
    passwordInput.insertAdjacentElement("afterend", issueList);
    return issueList;
  };

  const setupDynamicPasswordIssues = (form) => {
    const passwordInput = form.querySelector('input[name="password1"], input[name="new_password1"]');
    const passwordConfirmInput = form.querySelector('input[name="password2"], input[name="new_password2"]');

    if (!passwordInput || !passwordConfirmInput) {
      return;
    }

    const hideNode = (node) => {
      node.classList.add("hidden");
      node.setAttribute("aria-hidden", "true");
      node.hidden = true;
      node.style.display = "none";
    };

    const existingHintNode = form.querySelector("#id_password1_helptext, #id_new_password1_helptext");
    if (existingHintNode) {
      hideNode(existingHintNode);
    }

    const maybeRuleNodes = form.querySelectorAll("small, p, ul, .helptext");
    maybeRuleNodes.forEach((node) => {
      const text = (node.textContent || "").toLowerCase();
      const matchesRuleText = PASSWORD_RULE_MARKERS.some((marker) => text.includes(marker));
      if (matchesRuleText) {
        hideNode(node);
      }
    });

    const issueList = ensureIssueList(passwordInput);
    let shouldValidate = false;

    const renderIssues = () => {
      if (!shouldValidate) {
        issueList.classList.add("hidden");
        issueList.hidden = true;
        issueList.style.display = "none";
        issueList.innerHTML = "";
        return;
      }

      const issues = getPasswordIssues(passwordInput.value, form);
      if (!issues.length) {
        issueList.classList.add("hidden");
        issueList.hidden = true;
        issueList.style.display = "none";
        issueList.innerHTML = "";
        return;
      }

      issueList.innerHTML = "";
      issues.forEach((issue) => {
        const item = document.createElement("li");
        item.textContent = issue;
        issueList.appendChild(item);
      });
      issueList.classList.remove("hidden");
      issueList.hidden = false;
      issueList.style.display = "";
    };

    passwordConfirmInput.addEventListener("focus", () => {
      if (passwordInput.value.trim().length > 0) {
        shouldValidate = true;
        renderIssues();
      }
    });

    passwordInput.addEventListener("input", () => {
      if (shouldValidate) {
        renderIssues();
      }
    });

    passwordConfirmInput.addEventListener("input", renderIssues);
  };

  const stylePasswordHelp = (form) => {
    const helpLists = form.querySelectorAll("ul, .helptext");
    helpLists.forEach((node) => {
      const text = (node.textContent || "").toLowerCase();
      if (!text.includes("password")) {
        return;
      }
      styleHintNode(node);
    });

    setupDynamicPasswordIssues(form);
  };

  authForms.forEach((form) => {
    form.querySelectorAll("input, textarea").forEach(applyInputBehavior);
    stylePasswordHelp(form);
  });
});
