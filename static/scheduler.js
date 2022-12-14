"use strict";

const SCHEDULE_BLOCK_CLASS = "schedule-block";
const EDITABLE_BLOCK = "edit-block";
const SCHEDULE_TABLE_ID = "schedule-table";
const MINUTE_INC = 15;
const MINUTE_CHUNKS_PER_HR = 60 / MINUTE_INC;
const NUM_ROWS = parseInt(24 * MINUTE_CHUNKS_PER_HR);
const DAYS = [
    "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"
];
const NUM_DAYS = DAYS.length;

const BAD_COLOR = "#ffb0ab";
const GOOD_COLOR = "#73966f";

let isPressingDown = false;

var scheduleData = [...Array(NUM_ROWS)].map(e => Array(NUM_DAYS));

function submitSchedule() {
    let idx = 0;
    mapToEachScheduleCell((cell) => {
        if (!cell.classList.contains(EDITABLE_BLOCK)) return;
        // console.log(cell);
        const i = Math.floor(idx / NUM_DAYS);
        const j = idx % NUM_DAYS;
        scheduleData[i][j] = (cell.bgColor == BAD_COLOR)? 0 : 1;
        idx++;
    });

    const data = {"schedule": scheduleData, "minutes_per_element": MINUTE_INC, "days": DAYS};
    fetch(window.location.pathname, {
        method: "POST",
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => {
        if (res.ok && res.redirected) {
            window.location.href = res.url;
        }
    });
}

function postOverride(url, stateNum) {
    const data = {state: stateNum}
    fetch(url, {
        method: "POST",
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => {
        if (res.ok && res.redirected) {
            window.location.href = res.url;
        }
    });
}

function buildSchedule(saved) {
    scheduleData = saved.schedule || scheduleData
    const sch = document.getElementById("schedule-holster");
    sch.addEventListener('mouseleave', () => { isPressingDown = false; });
    const tab = buildScheduleTable();
    sch.appendChild(tab);
}

function wentDown(evt) {
    isPressingDown = true;
    recolor(evt);
}

function wentUp(evt) {
    isPressingDown = false;
    recolor(evt);
}

function buildScheduleTable() {
    const tab = document.createElement("table");
    tab.id = SCHEDULE_TABLE_ID
    // const th = tab.createTHead();
    const row = tab.insertRow();
    DAYS.forEach(d => {
        const td = row.insertCell();
        td.innerHTML = `<b>${d}</b>`;
        td.classList.add(SCHEDULE_BLOCK_CLASS);
    });
    const td = row.insertCell();
    td.innerHTML = "<b>Time Range</b>";
    td.classList.add(SCHEDULE_BLOCK_CLASS);

    for (let i = 0; i < NUM_ROWS; ++i) {
        const tr = tab.insertRow();
        for (let j = 0; j < NUM_DAYS; ++j) {
            const td = tr.insertCell();
            td.classList.add(SCHEDULE_BLOCK_CLASS);
            td.classList.add(EDITABLE_BLOCK);
            td.addEventListener('mousedown', wentDown);
            td.addEventListener('touchstart', wentDown);
            td.addEventListener('mousemove', recolor);
            td.addEventListener('touchmove', recolor);
            td.addEventListener('mouseup', wentUp);
            td.addEventListener('touchend', wentUp);
            td.bgColor = (scheduleData[i][j] == 1)? GOOD_COLOR : BAD_COLOR;
        }
        
        const total_minutes = i * MINUTE_INC;
        const hr = Math.floor(i / MINUTE_CHUNKS_PER_HR);
        const min = total_minutes % 60;

        const nextMin = (min + MINUTE_INC) % 60;
        const nextHr = (hr + (nextMin === 0? 1 : 0)) % 24;

        const timeCell = tr.insertCell();

        let tfmt = function(h, m) { return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}`; }
        timeCell.innerHTML = tfmt(hr, min);
        timeCell.innerHTML += ' - ' + tfmt(nextHr, nextMin);
    }
    return tab;
}

let lastColor = BAD_COLOR;
function recolor(evt) {
    evt = evt || window.event;
    if (evt.type.startsWith("mouse")) handleMouse(evt);
    else handleTouch(evt);
}

function handleTouch(evt) {
    const primaryTouch = evt.touches.item(0);
    const elt = document.elementFromPoint(
        primaryTouch.clientX,
        primaryTouch.clientY
    );
    if (evt.type == "touchstart") {
        lastColor = elt.bgColor;
    }
    if (isPressingDown) {
        const flipColor = (lastColor == BAD_COLOR) ? GOOD_COLOR : BAD_COLOR;
        if (elt.classList.contains(EDITABLE_BLOCK)) elt.bgColor = flipColor;
    }
}

function handleMouse(evt) {
    if (evt.type == "mousedown") {
        lastColor = evt.target.bgColor;
    }
    if (isPressingDown) {
        const flipColor = (lastColor == BAD_COLOR) ? GOOD_COLOR : BAD_COLOR;
        evt.target.bgColor = flipColor;
    }
}

function resetSchedule() {
    mapToEachScheduleCell((td) => {
        if (td.classList.contains(EDITABLE_BLOCK)) {
            td.bgColor = BAD_COLOR;
        }
    });
}

function mapToEachScheduleCell(funck) {
    const tab = document.getElementById(SCHEDULE_TABLE_ID);
    const rows = Array.from(tab.tBodies[0].children)
    rows.forEach((tr) => {
        Array.from(tr.cells).forEach(funck);
    });
}
