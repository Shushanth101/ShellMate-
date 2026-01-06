document.addEventListener('DOMContentLoaded', () => {
    // Typing Effect
    const terminalBody = document.getElementById('typing-demo');
    const textToType = [
        "> shellmate --login",
        "Authenticating...",
        "Welcome back, User!",
        "> I need a python script to scan duplicates",
        "Shelly: Sure! I can help with that.",
        "Shelly: Scanning file system...",
        "Shelly: Here is a script to find duplicates..."
    ];

    let lineIndex = 0;
    let charIndex = 0;

    function typeLine() {
        if (lineIndex < textToType.length) {
            const currentLine = textToType[lineIndex];

            if (charIndex < currentLine.length) {
                // Determine if it's a command or response for basic coloring logic if we parsed it
                // For now just append text
                if (charIndex === 0) {
                    const p = document.createElement('div');
                    p.id = `line-${lineIndex}`;
                    p.style.marginBottom = "5px";
                    terminalBody.appendChild(p);
                }
                const lineEl = document.getElementById(`line-${lineIndex}`);
                lineEl.textContent += currentLine.charAt(charIndex);
                charIndex++;
                setTimeout(typeLine, 50); // Typing speed
            } else {
                lineIndex++;
                charIndex = 0;
                setTimeout(typeLine, 800); // Pause between lines
            }
        }
    }

    typeLine();
});

// Copy Code Function
function copyCode() {
    const codeText = document.getElementById('install-code').innerText;
    navigator.clipboard.writeText(codeText).then(() => {
        const btn = document.querySelector('.copy-btn');
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = 'Copy';
        }, 2000);
    });
}
