// emotion-dashboard.jsx
import React, { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, BarChart, Bar
} from "recharts";
import { PieChart, Pie, Cell } from "recharts";
import axios from "axios";
import { useRef } from "react";

const insertNewlines = (text, maxLineLength = 80) => {
  const words = text.split(" ");
  const lines = [];
  let currentLine = "";

  for (const word of words) {
    if ((currentLine + word).length > maxLineLength) {
      lines.push(currentLine.trim());
      currentLine = word + " ";
    } else {
      currentLine += word + " ";
    }
  }
  lines.push(currentLine.trim());
  return lines.join("\n");
};

const CustomLegend = ({ payload, data }) => {
  const total = data.reduce((sum, e) => sum + e.value, 0);

  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {payload.map((entry, index) => {
        const label = entry.payload.name;
        const value = entry.payload.value ?? 0;
        const percent = total > 0 ? ((value / total) * 100).toFixed(1) : "0.0";

        return (
          <li key={`item-${index}`} style={{ marginBottom: 4 }}>
            <span style={{ color: entry.color, fontWeight: "bold" }}>■</span>{" "}
            {label} ({percent}%)
          </li>
        );
      })}
    </ul>
  );
};

const groupByDay = (data) => {
  return data.map(entry => ({
    date: entry.date,
    joy: entry.is_joy ?? 0,
    neutral: entry.is_neutral ?? 0,
    anxiety: entry.is_anxiety ?? 0,
    wound: entry.is_wound ?? 0,
    anger: entry.is_anger ?? 0,
    sadness: entry.is_sadness ?? 0,
    surprise: entry.is_surprise ?? 0,
  }));
};

const groupByDayFace = (data) => {
  return data.map(entry => ({
    date: entry.date,
    joy: entry.is_joy ?? 0,
    neutral: entry.is_neutral ?? 0,
    negative: entry.is_negative ?? 0,
  }));
};

const getFourWeeksData = (allWeeks, selected) => {
  const idx = allWeeks.findIndex(w =>
    w.year === selected.year &&
    w.month === selected.month &&
    w.week === selected.week
  );
  return idx >= 0 ? allWeeks.slice(Math.max(0, idx - 3), idx + 1) : [];
};

const generateWeeklyFeedback = (faceData, convoData) => {
  if (faceData.length === 0 || convoData.length === 0) return null;

  const avg = (arr, key) => arr.reduce((sum, d) => sum + d[key], 0) / arr.length;

  const avgFace = {
    joy: avg(faceData, "joy"),
    neutral: avg(faceData, "neutral"),
    negative: avg(faceData, "negative"),
  };

  const avgConvo = {
    joy: avg(convoData, "joy"),
    neutral: avg(convoData, "neutral"),
    negative: avg(convoData, "anxiety") + avg(convoData, "wound") + avg(convoData, "anger") + avg(convoData, "sadness") + avg(convoData, "surprise"),
    anxiety: avg(convoData, "anxiety"),
    wound: avg(convoData, "wound"),
    anger: avg(convoData, "anger"),
    sadness: avg(convoData, "sadness"),
    surprise: avg(convoData, "surprise"),
  };

  const feedback = [];

// ✅ 피드백 조건 통합
if (avgFace.negative > 0.4 && avgConvo.joy > 0.35) {
  feedback.push(
    "표정 분석 결과 부정 감정이 높게 나타난 반면, 대화에서는 긍정적인 표현이 다수 확인되었습니다. " +
    "이는 내면의 감정을 외부적으로 억제하거나 숨기고 있을 가능성을 시사합니다. " +
    "정서적 피로 또는 감정 표현의 제한이 누적될 수 있으므로 지속적인 관찰과 정서 지원이 필요합니다."
  );
}

if (avgFace.joy > 0.35 && avgConvo.negative > 0.4) {
  feedback.push(
    "표정 분석 결과는 전반적으로 긍정적인 반응을 보였으나, 대화 내용에서는 부정 감정이 다수 확인되었습니다. " +
    "이는 감정을 표정으로 드러내지 않고 억제하거나, 사회적 기대에 따라 표정을 통제하는 경향을 나타낼 수 있습니다. " +
    "감정 표현의 왜곡 가능성을 고려하여, 심층적인 정서 점검이 권장됩니다."
  );
}

if (avgFace.negative > 0.4 && avgConvo.negative > 0.4) {
  feedback.push(
    "표정과 대화 모두에서 부정 감정이 우세하게 나타났습니다. " +
    "이는 스트레스, 피로, 정서적 불균형의 신호일 수 있으며, 전반적인 감정 상태의 악화를 의미합니다. " +
    "조기 개입 및 심리적 지지가 필요한 상황으로 판단됩니다."
  );
}

if (avgFace.joy > 0.35 && avgConvo.joy > 0.35) {
  feedback.push(
    "표정과 대화 모두에서 긍정 감정이 안정적으로 나타났습니다. " +
    "정서적 균형이 유지되고 있으며, 심리적 건강 상태도 양호한 편으로 보입니다. " +
    "긍정 감정이 지속될 수 있도록 일상 속 감정 자극 환경을 유지하는 것이 좋습니다."
  );
}

if (Math.abs(avgFace.negative - avgFace.joy) < 0.1 && avgFace.negative > 0.3 && avgFace.joy > 0.3) {
  feedback.push(
    "표정에서 긍정과 부정 감정이 거의 비슷한 수준으로 나타났습니다. " +
    "이는 복합적이거나 모순적인 정서 상태를 나타낼 수 있으며, 감정의 양가성 또는 내적 갈등의 신호일 수 있습니다. " +
    "보다 정교한 감정 분석과 지속적인 관찰이 요구됩니다."
  );
}

// 중립 감정이 높으나 긍정/부정도 일정 이상 → 감정 억제형
if (
  (avgFace.neutral > 0.5 || avgConvo.neutral > 0.5) &&
  (avgFace.joy > 0.3 || avgFace.negative > 0.3 || avgConvo.joy > 0.3 || avgConvo.negative > 0.3)
) {
  feedback.push(
    "중립 감정이 우세하지만, 긍정 또는 부정 감정도 함께 감지되고 있습니다. " +
    "이는 내면의 감정을 외부로 드러내지 않으려는 표현 억제의 가능성을 시사합니다. " +
    "정서적 거리두기나 방어기제의 징후일 수 있으므로, 신중한 접근이 필요합니다."
  );
}

// 중립 감정이 우세하고 긍/부정 모두 매우 낮음 → 무감정형
if (
  (avgFace.neutral > 0.5 || avgConvo.neutral > 0.5) &&
  avgFace.joy < 0.2 && avgFace.negative < 0.2 &&
  avgConvo.joy < 0.2 && avgConvo.negative < 0.2
) {
  feedback.push(
    "표정과 대화 모두에서 감정의 명확한 반응이 나타나지 않고 있습니다. " +
    "이는 감정 에너지의 저하 또는 무기력 상태의 가능성을 내포할 수 있습니다. " +
    "심리적 활력 회복을 위한 환경적 변화나 정서 자극이 도움이 될 수 있습니다."
  );
}


if (
  avgFace.negative < 0.2 && avgFace.joy < 0.2 && avgFace.neutral < 0.6 &&
  avgConvo.negative < 0.2 && avgConvo.joy < 0.2 && avgConvo.neutral < 0.6
) {
  feedback.push(
    "표정과 대화 모두에서 감정의 표현이 전반적으로 낮게 나타났습니다. " +
    "이는 에너지 저하, 무감각 상태, 또는 표현 자체를 회피하려는 정서 방어기제로 해석될 수 있습니다. " +
    "감정 표현 유도 활동이나 비언어적 정서 소통 방식의 활용이 권장됩니다. "
  );
}

if (Math.abs(avgFace.joy - avgFace.neutral) < 0.05 && avgFace.joy > 0.3) {
  feedback.push(
    "표정에서 긍정과 중립 감정이 유사한 수준으로 나타났습니다. " +
    "편안하거나 수용적인 정서 상태일 수 있으며, 과도한 감정 반응 없이 일상을 받아들이는 경향이 나타납니다. " +
    "안정적인 정서 기반을 바탕으로 긍정 자극을 꾸준히 유지하는 것이 바람직합니다."
  );
}


  const highestNegative = Object.entries({
    불안: avgConvo.anxiety,
    상처: avgConvo.wound,
    분노: avgConvo.anger,
    슬픔: avgConvo.sadness,
    놀람: avgConvo.surprise
  }).sort((a, b) => b[1] - a[1])[0];

  if (avgConvo.negative > 0.4 && highestNegative[1] > 0.15) {
    feedback.push(
      `또한 부정 감정 중 '${highestNegative[0]}' 감정이 평균 ${(highestNegative[1] * 100).toFixed(1)}%로 가장 두드러지게 나타났습니다. ` +
      "해당 감정에 대한 정서적 개입이 권장됩니다."
    );
  }
  if (feedback.length === 0) {
    return " 최근 7일 감정 상태는 비교적 균형 있게 유지되고 있습니다.";
  }

  return feedback.join(" ");
};


const Dashboard = () => {
  const [userList, setUserList] = useState([]);
  const [userName, setUserName] = useState("");
  const [todayDate, setTodayDate] = useState("");
  const [recent7DaysFaceData, setRecent7DaysFaceData] = useState([]);
  const [recent7DaysData, setRecent7DaysData] = useState([]);
  const [weeklyEmotionData, setWeeklyEmotionData] = useState([]);
  const [weeklyFaceEmotionData, setWeeklyFaceEmotionData] = useState([]);
  const [selectedWeek, setSelectedWeek] = useState(null);
  const [warningReport, setWarningReport] = useState(null);
  const [guardians, setGuardians] = useState([]);
  const [dailyFaceData, setDailyFaceData] = useState([]);
  const [dailyConvoData, setDailyConvoData] = useState([]);
  const [weeklyFeedback, setWeeklyFeedback] = useState("");
  const [recommendationMessage, setRecommendationMessage] = useState("");
  const [wcWeeks, setWcWeeks] = useState([]);
  const [selectedWcWeek, setSelectedWcWeek] = useState(null);
  const [wcErrorMessage, setWcErrorMessage] = useState("");
  const [wcImageUrl, setWcImageUrl] = useState("");

 useEffect(() => {
    if (!userName) return;

    axios
      .get(`http://127.0.0.1:5000/api/wordcloud/conversation_weeks?user_id=${userName}`)
      .then((res) => {
        setWcWeeks(res.data);
        if (res.data.length > 0) {
          setSelectedWcWeek(res.data[res.data.length - 1]); // 최신 주차를 기본 선택
        }
      })
      .catch((err) => {
        console.error("주차 정보 로딩 실패", err);
      });
  }, [userName]);


  const getYesterdayDateString = () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return `${yesterday.getFullYear()}-${String(yesterday.getMonth() + 1).padStart(2, "0")}-${String(yesterday.getDate()).padStart(2, "0")}`;
  };

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/api/users").then(res => {
      console.log("사용자 목록:", res.data);
      setUserList(res.data);
    });
  }, []);

  useEffect(() => {
    if (!userName) return;
  
    axios.get(`http://127.0.0.1:5000/api/guardians/${userName}`)
      .then(res => setGuardians(res.data))
      .catch(err => {
        console.error("보호자 정보 로딩 실패", err);
        setGuardians([]);
      });
  }, [userName]);
  
  useEffect(() => {
    if (recent7DaysFaceData.length && recent7DaysData.length) {
      const feedbackRaw = generateWeeklyFeedback(recent7DaysFaceData, recent7DaysData);
      const feedbackWithNewlines = insertNewlines(feedbackRaw, 80);
      console.log("피드백 내용 ↓↓↓");
      console.log(feedbackWithNewlines);
      setWeeklyFeedback(feedbackWithNewlines);
    }
  }, [recent7DaysFaceData, recent7DaysData]);

 useEffect(() => {
    if (!selectedWcWeek || !userName) return;

    const fetchWordcloud = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/wordcloud/conversation", {
          params: {
            user_id: userName,
            year: selectedWcWeek.year,
            month: selectedWcWeek.month,
            week: selectedWcWeek.week
          },
          responseType: "blob",
        });

        const contentType = res.headers["content-type"];

        if (contentType.includes("application/json")) {
          // JSON 응답인 경우: 에러 메시지 처리
          const reader = new FileReader();
          reader.onload = () => {
            const json = JSON.parse(reader.result);
            setWcImageUrl(null);
            setWcErrorMessage(json.message || "단어 구름 데이터를 불러올 수 없습니다.");
          };
          reader.readAsText(res.data);
        } else {
          // 이미지인 경우
          const imageUrl = URL.createObjectURL(res.data);
          setWcImageUrl(imageUrl);
          setWcErrorMessage(null);
        }
      } catch (err) {
        setWcImageUrl(null);
        setWcErrorMessage("단어 구름 요청 중 오류가 발생했습니다.");
        console.error(err);
      }
    };

    fetchWordcloud();
  }, [selectedWcWeek, userName]);

  useEffect(() => {
    if (!userName) return;
  
    const yesterday = getYesterdayDateString();
  
    axios.get(`http://127.0.0.1:5000/api/avg/face?user_id=${userName}`)
        .then(res => {
        const yesterdayData = res.data.find(entry => entry.date === yesterday);
        if (yesterdayData) {
          setDailyFaceData([
            { name: "기쁨", value: yesterdayData.is_joy },
            { name: "중립", value: yesterdayData.is_neutral },
            { name: "부정", value: yesterdayData.is_negative }
          ]);
        } else {
          setDailyFaceData([]);
        }
        const recent7DaysFace = groupByDayFace(res.data).slice(-7);
        setRecent7DaysFaceData(recent7DaysFace);

      });
  
    axios.get(`http://127.0.0.1:5000/api/avg/conversation?user_id=${userName}`)
      .then(res => {
        const yesterdayData = res.data.find(entry => entry.date === yesterday);
        if (yesterdayData) {
          setDailyConvoData([
            { name: "기쁨", value: yesterdayData.is_joy },
            { name: "중립", value: yesterdayData.is_neutral },
            { name: "불안", value: yesterdayData.is_anxiety },
            { name: "상처", value: yesterdayData.is_wound },
            { name: "분노", value: yesterdayData.is_anger },
            { name: "슬픔", value: yesterdayData.is_sadness },
            { name: "놀람", value: yesterdayData.is_surprise }
          ]);
        } else {
          setDailyConvoData([]);
        }
        const recent7Days = groupByDay(res.data).slice(-7);
        setRecent7DaysData(recent7Days);
      });
  }, [userName]);
  
 

useEffect(() => {
  if (!dailyFaceData.length || !dailyConvoData.length) return;

  // 1. 표정: 부정 비율 계산
  const faceTotal = dailyFaceData.reduce((sum, e) => sum + e.value, 0);
  const faceMap = new Map(dailyFaceData.map(e => [e.name, e.value]));
  const faceNegative = faceMap.get('부정') || 0;
  const faceNegativeRatio = faceNegative / faceTotal;

  if (faceNegativeRatio < 0.3) {
    setRecommendationMessage('오늘은 추천 콘텐츠가 없습니다.');
    return;
  }

  // 2. 대화: 부정 감정 vs 긍정/중립 비교
  const poemEmotions = ['슬픔', '상처', '불안'];
  const classicEmotions = ['분노', '놀람'];
  const negativeEmotions = [...poemEmotions, ...classicEmotions];

  let negativeSum = 0;
  let positiveSum = 0;

  dailyConvoData.forEach(e => {
    if (negativeEmotions.includes(e.name)) {
      negativeSum += e.value;
    } else if (e.name === '기쁨' || e.name === '중립') {
      positiveSum += e.value;
    }
  });

  let msg = '';

  if (negativeSum > positiveSum) {
    const topNegative = dailyConvoData
      .filter(e => negativeEmotions.includes(e.name))
      .sort((a, b) => b.value - a.value)[0];

    const contentType = poemEmotions.includes(topNegative.name)
      ? '시'
      : '클래식 음악';

    msg = `어제 감정 분석 결과, 표정에서는 부정 감정이 높게 나타났고, 대화에서는 '${topNegative.name}' 감정이 우세하여 추천 콘텐츠로 ${contentType} 제공하였습니다.`;
  } else {
    msg = '오늘은 추천 콘텐츠가 없습니다.';
  }

  setRecommendationMessage(msg);
}, [dailyFaceData, dailyConvoData]);



  useEffect(() => {
    const today = new Date();
    const formatted = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
    setTodayDate(formatted);
  }, []);
  

  useEffect(() => {
    if (!userName) return;

    const fetchFaceData = async () => {
      try {
        const faceRes = await axios.get("http://127.0.0.1:5000/api/weekly/face_avg", {
          params: { user_id: userName }
        });

        setWeeklyFaceEmotionData(faceRes.data);

      } catch (err) {
        console.error("표정 주차별 데이터 로딩 실패", err);
      }
    };

    fetchFaceData();
  }, [userName]);


  useEffect(() => {
    if (!userName) return;

    const fetchData = async () => {
      try {
        const convoRes = await axios.get("http://127.0.0.1:5000/api/weekly/conversation_avg", {
          params: { user_id: userName }
        });

        setWeeklyEmotionData(convoRes.data);
        setSelectedWeek(convoRes.data[0]);

        const lastfour = convoRes.data.slice(-4);

        const summary = lastfour.map((week) => ({
          positive: week.avg_joy,
          neutral: week.avg_neutral,
          negative: week.avg_anxiety + week.avg_wound + week.avg_anger + week.avg_sadness + week.avg_surprise,
          anxiety: week.avg_anxiety,
          wound: week.avg_wound,
          anger: week.avg_anger,
          sadness: week.avg_sadness,
          surprise: week.avg_surprise,
        }));

      } catch (err) {
        console.error("데이터 로딩 실패", err);
        setRecent7DaysFaceData([]);
      }
    };
    fetchData();
  }, [userName]);

  const avg = (arr, key) => Math.round(arr.reduce((sum, d) => sum + d[key], 0) / arr.length);
  
  const weeklySummaryData = weeklyEmotionData.map(week => ({
    week: `${week.year}년 ${week.month}월 ${week.week}주차`,
    joy: week.avg_joy,
    neutral: week.avg_neutral,
    anxiety: week.avg_anxiety,
    wound: week.avg_wound,
    anger: week.avg_anger,
    sadness: week.avg_sadness,
    surprise: week.avg_surprise,
  }));

  const weeklyFaceSummaryData = weeklyFaceEmotionData.map(week => ({
    week: `${week.year}년 ${week.month}월 ${week.week}주차`,
    joy: week.avg_joy,
    neutral: week.avg_neutral,
    negative: week.avg_negative,
  }));

  const selectedFourWeeksConvo = selectedWeek
  ? getFourWeeksData(weeklyEmotionData, selectedWeek)
  : weeklyEmotionData.slice(-4);

  const selectedFourWeeksFace = selectedWeek
  ? getFourWeeksData(weeklyFaceEmotionData, selectedWeek)
  : weeklyFaceEmotionData.slice(-4);

  // ✅ 그다음 주차 선택 기준 4주
  const selectedFourWeeks = selectedWeek
    ? getFourWeeksData(weeklyEmotionData, selectedWeek)
    : weeklyEmotionData.slice(-4);

  const filteredWeeklyConvoData = selectedFourWeeks.map(week => ({
    week: `${week.year}년 ${week.month}월 ${week.week}주차`,
    joy: week.avg_joy,
    neutral: week.avg_neutral,
    anxiety: week.avg_anxiety,
    wound: week.avg_wound,
    anger: week.avg_anger,
    sadness: week.avg_sadness,
    surprise: week.avg_surprise,
  }));

  const filteredWeeklyFaceData = selectedFourWeeksFace.map(week => ({
    week: `${week.year}년 ${week.month}월 ${week.week}주차`,
    joy: week.avg_joy,
    neutral: week.avg_neutral,
    negative: week.avg_negative,
  }));

  const getUserNameById = (id) => {
    const user = userList.find((u) => u.id === Number(id));
    return user ? user.username : "사용자";
  };
const lastSentBiweeklyWarningRef = useRef("");

useEffect(() => {
  if (!userName || filteredWeeklyConvoData.length < 2 || filteredWeeklyFaceData.length < 2) return;

  const faceNegativeOk = filteredWeeklyFaceData
    .slice(-2)
    .every(week => week.negative > 0.4);

  if (!faceNegativeOk) {
    setWarningReport("");
    return; // 조건 만족 안 하면 종료
  }

  const convo2weeks = filteredWeeklyConvoData.slice(-2);

  const targetEmotions = [
    { key: "anxiety", label: "불안" },
    { key: "wound", label: "상처" },
    { key: "anger", label: "분노" },
    { key: "sadness", label: "슬픔" },
    { key: "surprise", label: "놀람" }
  ];

  // 각 감정별 최근 2주 평균 구함
  const emotionAverages = targetEmotions.map(({ key, label }) => {
    const avg =
      (convo2weeks[0][key] + convo2weeks[1][key]) / 2;
    return { key, label, avg };
  });

  // 평균이 가장 높은 감정 선택
  const top = emotionAverages.sort((a, b) => b.avg - a.avg)[0];

  if (top.avg < 0.3) {
    setWarningReport(""); // 우세하지 않으면 경고 안 띄움
    return;
  }

  const emotionMessages = {
    불안: "스트레스가 누적될 수 있으니 정서적 지지가 필요합니다.",
    상처: "자존감 저하가 우려되니 세심한 보살핌이 요구됩니다.",
    분노: "감정 조절이 필요한 시점입니다.",
    슬픔: "무기력감으로 이어지지 않도록 관심이 필요합니다.",
    놀람: "환경 변화나 충격 요인에 민감할 수 있습니다.",
  };

  const msg = `⚠️ 최근 2주간 표정에서 부정 감정이 지속적으로 높게 나타났고, 대화에서는 '${top.label}' 감정이 평균 ${(top.avg * 100).toFixed(1)}%로 우세하게 관찰되었습니다. ${emotionMessages[top.label]}`;
  setWarningReport(msg);
}, [filteredWeeklyConvoData, filteredWeeklyFaceData, userName]);



  console.log("주차별 표정 감정 평균 데이터:", weeklyFaceSummaryData);
  console.log("주차별 대화 감정 평균 데이터:", weeklySummaryData);


  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="mb-6 text-center">
        <h1 className="text-3xl font-bold">
           {getUserNameById(userName)}님의 심리 분석 리포트
        </h1>
        <p className="text-gray-600">
          주차별 감정 변화와 부정 감정의 세부 분석
        </p>
  
        {guardians.length > 0 && (
          <p className="mt-2 text-gray-700 text-sm">
            👥 보호자:{" "}
            {guardians.map((g, idx) => (
              <span key={idx}>
                {g.username} ({g.phone_number})
                {idx < guardians.length - 1 && ", "}
              </span>
            ))}
          </p>
        )}
      </header>
  
      <div className="flex justify-center mb-6">
        <label className="mr-4 font-semibold">🙋 사용자 선택:</label>
        <select
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          className="border rounded p-2"
        >
          <option value="">-- 선택하세요 --</option>
          {userList.map((u) => (
            <option key={u.id} value={u.id}>{u.username}
            </option>
          ))}
        </select>
      </div>      

      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-6">
          📅 어제의 감정 비율 ({getYesterdayDateString()})
        </h2>

        <div className="flex justify-center gap-12 flex-wrap">
        {/* 표정 */}
        <div className="bg-white shadow-md rounded p-4 w-[320px]">
              <h3 className="mb-4 font-semibold text-center"> 표정</h3>
              {dailyFaceData.length > 0 && dailyFaceData.some((d) => d.value > 0) ? (
                <>
                  <PieChart width={320} height={250}>
                    <Pie
                      data={dailyFaceData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                    >
                      {dailyFaceData.map((entry, index) => (
                        <Cell key={index} fill={["#FD6282", "#36A2EB", "#8ED973"][index % 3]} />
                      ))}
                    </Pie>
                  
                    <Legend 
                      layout="vertical"
                      verticalAlign="middle"
                      align="right"
                      iconType="square"
                      content={<CustomLegend data={dailyFaceData} />}
                    />
                  </PieChart>
                </>
              ) : (
                <p className="text-center text-gray-500">어제의 표정 데이터가 존재하지 않습니다.</p>
              )}
            </div>

            {/* 대화 */}
            <div className="bg-white shadow-md rounded p-4 w-[320px]">
              <h3 className="mb-4 font-semibold text-center"> 대화</h3>
              {dailyConvoData.length > 0 && dailyConvoData.some((d) => d.value > 0) ? (
                <>
                  <PieChart width={320} height={250}>
                    <Pie
                      data={dailyConvoData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                    >
                      {dailyConvoData.map((entry, index) => (
                        <Cell
                          key={index}
                          fill={
                            ["#FD6282", "#36A2EB", "#FECD57", "#4AC0C0", "#FF9F40", "#9966FF", "#8F9DB9"][index % 7]
                          }
                        />
                      ))}
                    </Pie>
 
                    <Legend 
                      layout="vertical"
                      verticalAlign="middle"
                      align="right"
                      iconType="square"
                      content={<CustomLegend data={dailyFaceData} />}
                    />
                  </PieChart>

                  {recommendationMessage && (
                     <div className="mt-4 text-center text-blue-800 font-medium">
                      {recommendationMessage}
                     </div>
                  )}
                </>
              ) : (
                <p className="text-center text-gray-500">어제의 대화 데이터가 존재하지 않습니다.</p>
              )}
            </div>
          </div>
      </section>

            
      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-4">📊 최근 7일 표정 감정 추이</h2>
        <BarChart width={800} height={300} data={recent7DaysFaceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(1)}%`}
          />

          <Legend />
          <Bar dataKey="joy" stackId="a" fill="#FD6282" name="기쁨" barSize={50}/>
          <Bar dataKey="neutral" stackId="a" fill="#36A2EB" name="중립" />
          <Bar dataKey="negative" stackId="a" fill="#8ED973" name="부정" />
        </BarChart>
      </section>

      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-4">📊 최근 7일 대화 감정 추이</h2>
        <BarChart width={800} height={300} data={recent7DaysData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(1)}%`}
          />

          <Legend />
          <Bar dataKey="joy" stackId="a" fill="#FD6282" name="기쁨" barSize={50}/>
          <Bar dataKey="neutral" stackId="a" fill="#36A2EB" name="중립" />
          <Bar dataKey="anxiety" stackId="a" fill="#FECD57" name="불안" />
          <Bar dataKey="wound" stackId="a" fill="#4AC0C0" name="상처" />
          <Bar dataKey="anger" stackId="a" fill="#FF9F40" name="분노" />
          <Bar dataKey="sadness" stackId="a" fill="#9966FF" name="슬픔" />
          <Bar dataKey="surprise" stackId="a" fill="#8F9DB9" name="놀람" />
        </BarChart>
      </section>

      {weeklyFeedback && (
        <>
          <div className="flex justify-center mt-6">
            <div className="w-[600px] px-4 bg-yellow-50 border border-yellow-300 text-yellow-900 p-4 rounded font-semibold text-left leading-relaxed">
              {weeklyFeedback.split("\n").map((line, idx) => (
                <p key={idx} className="mb-2">{line}</p>
              ))}
            </div>
          </div>

          {/* 드롭다운과의 간격을 위한 빈 줄 */}
          <div style={{ height: "1.5rem" }}></div>
        </>
      )}

            {/* 📅 어제 감정 원그래프 밑에 주차 선택 드롭다운 */}
          <div className="flex justify-center mt-4 mb-6">
            <label className="mr-3 font-semibold"> 📅 주차 선택:</label>
            
            <select
                  className="border rounded p-2"
                  value={selectedWeek ? `${selectedWeek.year}-${selectedWeek.month}-${selectedWeek.week}` : ""}
                  onChange={(e) => {
                        const [year, month, week] = e.target.value.split("-").map(Number);
                        const target = weeklyEmotionData.find(w => w.year === year && w.month === month && w.week === week);
                        setSelectedWeek(target);
                  }}
            >
                  {weeklyEmotionData.map((week, idx) => (
                        <option key={idx} value={`${week.year}-${week.month}-${week.week}`}>
                              {`${week.year}년 ${week.month}월 ${week.week}주차`}
                        </option>
                  ))}
            </select>
      </div>
     
      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-4">📊 주차별 표정 감정 평균</h2>
        <BarChart width={800} height={300} data={filteredWeeklyFaceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(1)}%`}
          />
          <Legend />
          <Bar dataKey="joy" stackId="a" fill="#FD6282" name="기쁨" barSize={50} />
          <Bar dataKey="neutral" stackId="a" fill="#36A2EB" name="중립" />
          <Bar dataKey="negative" stackId="a" fill="#8ED973" name="부정" />
        </BarChart>
      </section>



      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-4">📊 주차별 대화 감정 평균</h2>
        <BarChart width={800} height={300} data={filteredWeeklyConvoData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(1)}%`}
          />
          <Legend />
          <Bar dataKey="joy" stackId="a" fill="#FD6282" name="기쁨" barSize={50}/>
          <Bar dataKey="neutral" stackId="a" fill="#36A2EB" name="중립" />
          <Bar dataKey="anxiety" stackId="a" fill="#FECD57" name="불안" />
          <Bar dataKey="wound" stackId="a" fill="#4AC0C0" name="상처" />
          <Bar dataKey="anger" stackId="a" fill="#FF9F40" name="분노" />
          <Bar dataKey="sadness" stackId="a" fill="#9966FF" name="슬픔" />
          <Bar dataKey="surprise" stackId="a" fill="#8F9DB9" name="놀람" />
        </BarChart>
            
            {warningReport && (
               <div style={{ marginTop: "16px", padding: "12px", border: "1px solid red", borderRadius: "8px", backgroundColor: "#ffe5e5", color: "#a30000", maxWidth: "800px"}}>
             <strong>{warningReport}</strong>

          
        </div>
      )}
   </section>
      <section className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold text-center mb-4">💬 주차별 자주 사용하는 단어</h2>

        {/* 주차 선택 드롭다운 */}
        <div className="flex justify-center mb-4">
          {wcWeeks.length > 0 ? (
            <select
              className="border rounded p-2"
              value={selectedWcWeek ? `${selectedWcWeek.year}-${selectedWcWeek.month}-${selectedWcWeek.week}` : ""}
              onChange={(e) => {
                const [year, month, week] = e.target.value.split("-").map(Number);
                setSelectedWcWeek({ year, month, week });
              }}
            >
              {wcWeeks.map((w, idx) => (
                <option key={idx} value={`${w.year}-${w.month}-${w.week}`}>
                  {`${w.year}년 ${w.month}월 ${w.week}주차`}
                </option>
              ))}
            </select>
          ) : (
            <p className="text-gray-500 text-center">해당 사용자의 주차 정보가 없습니다.</p>
          )}
        </div>


        {/* 단어 구름 이미지 */}
        <div className="flex justify-center">
          {wcWeeks.length === 0 ? null : selectedWcWeek ? (
            wcErrorMessage ? (
              <p className="text-red-500 text-center">{wcErrorMessage}</p>
            ) : wcImageUrl ? (
              <img
                key={wcImageUrl}
                src={wcImageUrl}
                alt="wordcloud"
                className="rounded shadow-md"
                style={{ width: "800px", height: "auto" }}
              />
            ) : (
              <p className="text-gray-400 text-center">단어 구름 이미지를 불러오는 중입니다...</p>
            )
          ) : (
            <p className="text-gray-500 text-center">주차를 선택하면 단어 구름이 표시됩니다.</p>
          )}
        </div>

      </section>

    </div>
  );
};

export default Dashboard;




