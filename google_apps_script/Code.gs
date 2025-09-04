/**
 * ローグライク演習フレームワーク v1.2.3 
 * Google Apps Script Webhook エンドポイント
 * 
 * 学生のセッションログを受け取り、Google Sheetsに自動記録します
 */

// ===== 設定 =====
const SPREADSHEET_BASE_NAME = 'ローグライク演習_セッションログ';
const SHARED_FOLDER_ID = null; // 共有フォルダID（設定により変更可能）
const HEADER_ROW = [
  '学生ID', 'ステージ', '終了日時', '完了フラグ', 'アクション数', 'コード行数', '解法コード'
];

/**
 * テスト用の簡単な関数 - Google Apps Scriptエディターで実行
 */
function simpleTest() {
  Logger.log('=== テスト開始 ===');
  
  try {
    // 1. 基本的なスプレッドシート作成テスト
    Logger.log('スプレッドシート作成テスト開始');
    const testName = 'テスト_ローグライク_' + new Date().getTime();
    const spreadsheet = SpreadsheetApp.create(testName);
    const sheet = spreadsheet.getActiveSheet();
    sheet.getRange(1, 1).setValue('テストデータ');
    
    Logger.log(`スプレッドシート作成成功: ${spreadsheet.getId()}`);
    Logger.log(`スプレッドシート名: ${testName}`);
    
    // 2. フォルダIDチェック
    Logger.log(`フォルダID設定: ${SHARED_FOLDER_ID}`);
    
    // 3. フォルダ移動テスト（設定されている場合）
    if (SHARED_FOLDER_ID && SHARED_FOLDER_ID !== null) {
      Logger.log('フォルダ移動テスト開始');
      const file = DriveApp.getFileById(spreadsheet.getId());
      const folder = DriveApp.getFolderById(SHARED_FOLDER_ID);
      file.moveTo(folder);
      Logger.log('フォルダ移動成功');
    } else {
      Logger.log('フォルダID未設定 - ルートディレクトリに作成');
    }
    
    Logger.log('=== テスト完了 ===');
    return 'テスト完了';
    
  } catch (error) {
    Logger.log(`=== テストエラー ===`);
    Logger.log(`エラー詳細: ${error.toString()}`);
    Logger.log(`エラースタック: ${error.stack}`);
    return `エラー: ${error.toString()}`;
  }
}

/**
 * HTTPリクエストを受け取るメインハンドラー
 * @param {Object} e - リクエストオブジェクト
 * @return {Object} レスポンス
 */
function doPost(e) {
  try {
    Logger.log('=== doPost 開始 ===');
    Logger.log(`リクエストタイプ: ${typeof e}`);
    Logger.log(`e.postData: ${JSON.stringify(e.postData)}`);
    
    // POSTデータを解析
    const requestData = JSON.parse(e.postData.contents);
    Logger.log(`解析されたリクエストデータ: ${JSON.stringify(requestData)}`);
    
    // ログデータを検証
    Logger.log('データ検証開始');
    if (!validateLogData(requestData)) {
      Logger.log('データ検証失敗');
      return createResponse(400, { error: '無効なログデータです' });
    }
    Logger.log('データ検証成功');
    
    // スプレッドシートに記録
    Logger.log('スプレッドシート記録開始');
    const result = recordLogToSheet(requestData);
    Logger.log(`記録結果: ${JSON.stringify(result)}`);
    
    if (result.success) {
      Logger.log(`ログ記録成功: ${requestData.student_id} - ${requestData.stage_id}`);
      return createResponse(200, { 
        success: true, 
        message: 'ログを記録しました',
        row_number: result.rowNumber
      });
    } else {
      Logger.log(`ログ記録失敗: ${result.error}`);
      return createResponse(500, { error: result.error });
    }
    
  } catch (error) {
    Logger.log(`=== doPost エラー ===`);
    Logger.log(`エラー詳細: ${error.toString()}`);
    Logger.log(`エラースタック: ${error.stack}`);
    return createResponse(500, { error: 'サーバーエラーが発生しました' });
  }
}

/**
 * GETリクエスト用ハンドラー（テスト用）
 * @param {Object} e - リクエストオブジェクト
 * @return {Object} レスポンス
 */
function doGet(e) {
  const html = `
    <html>
      <head><title>ローグライク演習ログ受信システム</title></head>
      <body>
        <h2>🎮 ローグライク演習フレームワーク v1.2.3</h2>
        <p>✅ Webhookエンドポイントは正常に動作しています</p>
        <p>📊 ステージ別スプレッドシート: <strong>${SPREADSHEET_BASE_NAME}_[ステージID]</strong></p>
        <p>🔗 ログアップロード用URL: <code>${ScriptApp.getService().getUrl()}</code></p>
        <hr>
        <p><small>学生の皆さん: <code>python upload.py --setup</code> でこのURLを設定してください</small></p>
      </body>
    </html>
  `;
  return HtmlService.createHtmlOutput(html);
}

/**
 * ログデータの妥当性検証（v1.2.2セッション用7項目）
 * @param {Object} data - ログデータ
 * @return {boolean} 有効かどうか
 */
function validateLogData(data) {
  Logger.log(`=== バリデーション開始 ===`);
  Logger.log(`検証対象データ: ${JSON.stringify(data)}`);
  
  // v1.2.2セッション用必須フィールド
  const requiredFields = [
    'student_id', 'stage_id', 'end_time', 'solve_code', 
    'completed_successfully', 'action_count', 'code_lines'
  ];
  
  // 必須フィールドの存在確認
  for (const field of requiredFields) {
    if (!(field in data)) {
      Logger.log(`必須フィールドが不足: ${field}`);
      return false;
    }
  }
  Logger.log('必須フィールドチェック: OK');
  
  // 学生ID形式確認（6桁数字+1英字）
  if (!/^\d{6}[A-Z]$/.test(data.student_id)) {
    Logger.log(`無効な学生ID形式: ${data.student_id}`);
    return false;
  }
  Logger.log(`学生IDチェック: OK (${data.student_id})`);
  
  // ステージ名確認
  if (!/^(stage\d{2}|test)$/.test(data.stage_id)) {
    Logger.log(`無効なステージ名: ${data.stage_id}`);
    return false;
  }
  Logger.log(`ステージIDチェック: OK (${data.stage_id})`);
  
  // 日時形式確認（ISO形式）
  try {
    new Date(data.end_time);
    Logger.log(`日時チェック: OK (${data.end_time})`);
  } catch (error) {
    Logger.log(`無効な日時形式: ${data.end_time}`);
    return false;
  }
  
  Logger.log(`=== バリデーション完了: すべてOK ===`);
  return true;
}

/**
 * ログをスプレッドシートに記録
 * @param {Object} logData - ログデータ
 * @return {Object} 記録結果
 */
function recordLogToSheet(logData) {
  try {
    Logger.log('=== recordLogToSheet 開始 ===');
    
    // デバッグ：受信データをログ出力
    Logger.log(`受信データ: ${JSON.stringify(logData)}`);
    Logger.log(`ステージID: ${logData.stage_id}`);
    Logger.log(`学生ID: ${logData.student_id}`);
    Logger.log(`終了日時: ${logData.end_time}`);
    
    // データ形式チェック
    if (!logData.stage_id) {
      Logger.log('エラー: stage_idが未定義');
      return { success: false, error: 'stage_idが未定義' };
    }
    
    // スプレッドシートを取得または作成（ステージ別）
    Logger.log('スプレッドシート取得開始');
    const sheet = getOrCreateSheet(logData.stage_id);
    Logger.log('スプレッドシート取得成功');
    
    // ヘッダー行の確認・作成
    ensureHeaderRow(sheet);
    
    // ログデータを行データに変換
    const rowData = convertLogDataToRow(logData);
    
    // 既存データの確認（学生ID + ステージの組み合わせ）
    const existingRowIndex = findExistingRecord(sheet, logData.student_id, logData.stage_id);
    
    let targetRow;
    let isUpdate = false;
    
    if (existingRowIndex > 0) {
      // 既存レコードを上書き
      targetRow = existingRowIndex;
      isUpdate = true;
      Logger.log(`既存レコードを上書き: 学生ID=${logData.student_id}, ステージ=${logData.stage_id}, 行=${targetRow}`);
    } else {
      // 新規レコードを追加
      const lastRow = sheet.getLastRow();
      targetRow = lastRow + 1;
      Logger.log(`新規レコードを追加: 学生ID=${logData.student_id}, ステージ=${logData.stage_id}, 行=${targetRow}`);
    }
    
    // 範囲を指定してデータを挿入
    const range = sheet.getRange(targetRow, 1, 1, rowData.length);
    range.setValues([rowData]);
    
    // データ検証（テスト用ログを除く）
    if (logData.stage_id !== 'test') {
      // セルの書式設定
      formatNewRow(sheet, targetRow, logData);
    }
    
    return { 
      success: true, 
      rowNumber: targetRow,
      sheetName: sheet.getName(),
      isUpdate: isUpdate
    };
    
  } catch (error) {
    Logger.log(`シート記録エラー: ${error.toString()}`);
    return { 
      success: false, 
      error: error.toString() 
    };
  }
}

/**
 * 既存レコードを検索（学生ID + ステージの組み合わせ）
 * @param {Sheet} sheet - スプレッドシート
 * @param {string} studentId - 学生ID
 * @param {string} stageId - ステージID
 * @return {number} 既存レコードの行番号（見つからない場合は0）
 */
function findExistingRecord(sheet, studentId, stageId) {
  try {
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) {
      // ヘッダー行のみの場合
      return 0;
    }
    
    // データ範囲を取得（ヘッダー行を除く）
    const dataRange = sheet.getRange(2, 1, lastRow - 1, 2); // 学生ID（列1）とステージ（列2）のみ
    const values = dataRange.getValues();
    
    // 学生ID + ステージの組み合わせを検索
    for (let i = 0; i < values.length; i++) {
      const rowStudentId = values[i][0]; // 学生ID（列1）
      const rowStageId = values[i][1];   // ステージ（列2）
      
      if (rowStudentId === studentId && rowStageId === stageId) {
        return i + 2; // データ行の実際の行番号（ヘッダー行+1 + インデックス）
      }
    }
    
    return 0; // 見つからない
    
  } catch (error) {
    Logger.log(`既存レコード検索エラー: ${error.toString()}`);
    return 0;
  }
}

/**
 * ステージ別スプレッドシート名を生成
 * @param {string} stageId - ステージID
 * @return {string} スプレッドシート名
 */
function getSpreadsheetName(stageId) {
  return `${SPREADSHEET_BASE_NAME}_${stageId}`;
}

/**
 * スプレッドシートを取得または新規作成
 * @param {string} stageId - ステージID
 * @return {Sheet} スプレッドシート
 */
function getOrCreateSheet(stageId) {
  const spreadsheetName = getSpreadsheetName(stageId);
  
  // 既存のスプレッドシートを検索
  const files = DriveApp.getFilesByName(spreadsheetName);
  
  if (files.hasNext()) {
    // 既存スプレッドシートを使用
    const file = files.next();
    const spreadsheet = SpreadsheetApp.openById(file.getId());
    return spreadsheet.getActiveSheet();
  } else {
    // 新規スプレッドシート作成
    const spreadsheet = SpreadsheetApp.create(spreadsheetName);
    const sheet = spreadsheet.getActiveSheet();
    sheet.setName('セッションログ');
    
    // 共有フォルダに移動（設定されている場合）
    if (SHARED_FOLDER_ID) {
      try {
        const file = DriveApp.getFileById(spreadsheet.getId());
        const folder = DriveApp.getFolderById(SHARED_FOLDER_ID);
        file.moveTo(folder);
        Logger.log(`スプレッドシートを共有フォルダに移動: ${spreadsheetName}`);
      } catch (error) {
        Logger.log(`共有フォルダ移動エラー: ${error.toString()}`);
      }
    }
    
    Logger.log(`新しいスプレッドシートを作成しました: ${spreadsheetName}`);
    return sheet;
  }
}

/**
 * ヘッダー行の確認・作成
 * @param {Sheet} sheet - スプレッドシート
 */
function ensureHeaderRow(sheet) {
  if (sheet.getLastRow() === 0) {
    // ヘッダー行を追加
    const headerRange = sheet.getRange(1, 1, 1, HEADER_ROW.length);
    headerRange.setValues([HEADER_ROW]);
    
    // ヘッダー行のスタイル設定
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#e1f5fe');
    
    // 列幅の調整
    sheet.autoResizeColumns(1, HEADER_ROW.length - 1); // 解法コード列以外
    
    // 解法コード列（最後の列）の幅を狭く設定して折りたたみ
    const lastColumn = HEADER_ROW.length;
    sheet.setColumnWidth(lastColumn, 80); // 80px幅に設定
    
    // 解法コード列にテキスト折り返しを設定
    const codeColumn = sheet.getRange(1, lastColumn, sheet.getMaxRows(), 1);
    codeColumn.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);
    
    // フィルターを有効化
    sheet.getRange(1, 1, 1, HEADER_ROW.length).createFilter();
    
    Logger.log('ヘッダー行を作成しました（解法コード列は折りたたみ設定）');
  }
}

/**
 * ログデータを行データに変換（v1.2.2セッション用7項目）
 * @param {Object} logData - ログデータ
 * @return {Array} 行データ配列
 */
function convertLogDataToRow(logData) {
  // 完了フラグを適切に変換（boolean → ✅/❌）
  let completedFlag = '';
  if (logData.completed_successfully === true) {
    completedFlag = '✅';
  } else if (logData.completed_successfully === false) {
    completedFlag = '❌';
  }
  
  // アクション数とコード行数を適切に変換（0も含める）
  const actionCount = (logData.action_count !== null && logData.action_count !== undefined) 
    ? logData.action_count.toString() : '';
  const codeLines = (logData.code_lines !== null && logData.code_lines !== undefined) 
    ? logData.code_lines.toString() : '';
  
  return [
    logData.student_id,
    logData.stage_id,
    new Date(logData.end_time),
    completedFlag,
    actionCount,
    codeLines,
    logData.solve_code || ''  // 解法コードを最後に移動
  ];
}

/**
 * 新しい行の書式設定
 * @param {Sheet} sheet - スプレッドシート
 * @param {number} rowNumber - 行番号
 * @param {Object} logData - ログデータ
 */
function formatNewRow(sheet, rowNumber, logData) {
  try {
    const range = sheet.getRange(rowNumber, 1, 1, HEADER_ROW.length);
    
    // ログレベルに応じた色分け
    let backgroundColor = '#ffffff'; // デフォルト白
    
    switch (logData.log_level) {
      case 'ERROR':
      case 'CRITICAL':
        backgroundColor = '#ffebee'; // 薄赤
        break;
      case 'WARNING':
        backgroundColor = '#fff3e0'; // 薄オレンジ
        break;
      case 'DEBUG':
        backgroundColor = '#f5f5f5'; // 薄灰色
        break;
      // INFO（デフォルト）は白のまま
    }
    
    if (backgroundColor !== '#ffffff') {
      range.setBackground(backgroundColor);
    }
    
    // 日時列の書式設定
    const dateRange = sheet.getRange(rowNumber, 3); // 日時列（3列目）
    dateRange.setNumberFormat('yyyy/mm/dd hh:mm:ss');
    
  } catch (error) {
    Logger.log(`書式設定エラー: ${error.toString()}`);
  }
}

/**
 * レスポンス作成
 * @param {number} statusCode - HTTPステータスコード
 * @param {Object} data - レスポンスデータ
 * @return {Object} レスポンス
 */
function createResponse(statusCode, data) {
  const response = ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
  
  // CORS対応（Google Apps Scriptでは個別設定）
  // NOTE: ContentServiceではCORSヘッダーの設定は制限されています
  
  return response;
}

/**
 * 統計情報取得（テスト・管理用）
 */
function getLogStatistics() {
  try {
    const sheet = getOrCreateSheet();
    const lastRow = sheet.getLastRow();
    
    if (lastRow <= 1) {
      return { totalLogs: 0, students: 0, stages: 0 };
    }
    
    // データ範囲取得
    const dataRange = sheet.getRange(2, 1, lastRow - 1, HEADER_ROW.length);
    const values = dataRange.getValues();
    
    const students = new Set();
    const stages = new Set();
    
    values.forEach(row => {
      students.add(row[0]); // 学生ID
      stages.add(row[2]);   // ステージ
    });
    
    const stats = {
      totalLogs: lastRow - 1,
      students: students.size,
      stages: stages.size,
      lastUpdate: new Date().toISOString()
    };
    
    Logger.log(`統計情報: ${JSON.stringify(stats)}`);
    return stats;
    
  } catch (error) {
    Logger.log(`統計取得エラー: ${error.toString()}`);
    return { error: error.toString() };
  }
}

/**
 * シートリセット機能（テスト用）
 * @param {string} stageId - ステージID
 * @return {boolean} リセット成功/失敗
 */
function resetSheet(stageId) {
  try {
    const spreadsheetName = getSpreadsheetName(stageId);
    const files = DriveApp.getFilesByName(spreadsheetName);
    
    if (files.hasNext()) {
      const file = files.next();
      const spreadsheet = SpreadsheetApp.openById(file.getId());
      const sheet = spreadsheet.getActiveSheet();
      
      // 全データをクリア
      sheet.clear();
      
      // ヘッダー行を再作成
      ensureHeaderRow(sheet);
      
      Logger.log(`シートをリセットしました: ${spreadsheetName}`);
      return true;
    } else {
      Logger.log(`シートが見つかりません: ${spreadsheetName}`);
      return false;
    }
  } catch (error) {
    Logger.log(`シートリセットエラー: ${error.toString()}`);
    return false;
  }
}

/**
 * 全シートリセット機能（管理者用）
 * 使用方法: Google Apps Scriptエディターで resetAllSheets() を実行
 */
function resetAllSheets() {
  const stages = ['stage01', 'stage02', 'stage03', 'stage04', 'stage05'];
  let resetCount = 0;
  
  stages.forEach(stage => {
    if (resetSheet(stage)) {
      resetCount++;
    }
  });
  
  Logger.log(`${resetCount} 個のシートをリセットしました`);
  return resetCount;
}