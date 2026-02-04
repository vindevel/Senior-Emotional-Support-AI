import logo from './logo.svg';
import './App.css';

import React from "react";

const App = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-2xl">
        <h1 className="text-2xl font-bold text-center text-gray-800">🧠 심리 상태 리포트</h1>

        {/* 심리 점수 표시 */}
        <div className="mt-4 p-4 bg-blue-100 rounded-lg">
          <p className="text-lg font-semibold">현재 스트레스 점수: <span className="text-blue-600">75 / 100</span></p>
        </div>

        {/* 분석 결과 */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
          <h2 className="text-lg font-bold text-gray-700">📌 분석 결과</h2>
          <p className="text-gray-600 mt-2">최근 감정 변화가 크며, 스트레스 수준이 높습니다.</p>
        </div>

        {/* 추천 행동 */}
        <div className="mt-4 p-4 bg-green-50 rounded-lg border">
          <h2 className="text-lg font-bold text-green-700">✅ 추천 행동</h2>
          <ul className="list-disc ml-4 text-gray-600">
            <li>산책 30분 하기</li>
            <li>명상 및 심호흡 연습</li>
            <li>가벼운 음악 듣기</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default App;
