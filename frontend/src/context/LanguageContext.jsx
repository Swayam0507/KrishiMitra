import React, { createContext, useContext, useState } from 'react'

const TRANSLATIONS = {
  en: {
    nav: {
      dashboard: 'Dashboard', farms: 'My Farms', plots: 'Plots', crops: 'Crops',
      activities: 'Activities', workers: 'Workers', expenses: 'Expenses',
      inventory: 'Inventory', disease: 'Disease Detection', recommendation: 'Crop Recommendation',
      irrigation: 'Smart Irrigation', weather: 'Weather', advisor: 'AI Advisor',
      assistant: 'AI Assistant', alerts: 'Alerts', analytics: 'Analytics',
      reports: 'Reports', sensors: 'Sensors', settings: 'Settings',
    },
    common: {
      save: 'Save', cancel: 'Cancel', delete: 'Delete', edit: 'Edit', add: 'Add',
      loading: 'Loading...', submit: 'Submit', close: 'Close', back: 'Back',
      confirm: 'Confirm', yes: 'Yes', no: 'No', search: 'Search',
      filter: 'Filter', export: 'Export', refresh: 'Refresh', view: 'View',
      create: 'Create', update: 'Update', remove: 'Remove',
      modelNotTrained: 'MODEL NOT TRAINED',
      simulatedData: 'SIMULATED DATA',
      demoMode: 'DEMO MODE',
    },
    dashboard: {
      title: 'Dashboard', subtitle: 'Your farm at a glance',
      farmHealth: 'Farm Health', cropHealth: 'Crop Health',
      diseaseRisk: 'Disease Risk', waterEfficiency: 'Water Efficiency',
      sustainability: 'Sustainability', todayRecs: "Today's Recommendations",
      criticalAlerts: 'Critical Alerts', weatherConditions: 'Weather',
      sensorStatus: 'Sensor Status', recentActivities: 'Recent Activities',
      aiInsights: 'AI Insights',
    },
    disease: {
      title: 'Disease Detection', upload: 'Upload Leaf Image',
      drag: 'Drag & drop or click to upload', analyze: 'Analyze',
      result: 'Disease Detected', confidence: 'Confidence', risk: 'Risk',
      recommendations: 'Recommended Actions', history: 'Prediction History',
      noModel: 'MODEL NOT TRAINED — train the model to get predictions',
      lowConfidence: 'Low confidence — upload a clearer image',
      gradcam: 'AI Attention Map',
    },
    alerts: {
      title: 'Alerts', markRead: 'Mark Read', markAllRead: 'Mark All Read',
      noAlerts: 'No alerts', critical: 'Critical', high: 'High',
      medium: 'Medium', low: 'Low',
    },
  },
  hi: {
    nav: {
      dashboard: 'डैशबोर्ड', farms: 'मेरे खेत', plots: 'प्लॉट', crops: 'फसलें',
      activities: 'गतिविधियां', workers: 'मजदूर', expenses: 'खर्च',
      inventory: 'भंडार', disease: 'रोग पहचान', recommendation: 'फसल सुझाव',
      irrigation: 'सिंचाई', weather: 'मौसम', advisor: 'AI सलाहकार',
      assistant: 'AI सहायक', alerts: 'अलर्ट', analytics: 'विश्लेषण',
      reports: 'रिपोर्ट', settings: 'सेटिंग',
    },
    common: {
      save: 'सहेजें', cancel: 'रद्द', delete: 'हटाएं', edit: 'संपादन', add: 'जोड़ें',
      loading: 'लोड हो रहा है...', submit: 'जमा करें', close: 'बंद करें', back: 'वापस',
      confirm: 'पुष्टि', yes: 'हाँ', no: 'नहीं', search: 'खोजें',
      filter: 'फ़िल्टर', export: 'निर्यात', refresh: 'रिफ्रेश', view: 'देखें',
      create: 'बनाएं', update: 'अपडेट', remove: 'हटाएं',
      modelNotTrained: 'मॉडल प्रशिक्षित नहीं',
      simulatedData: 'अनुकरणीय डेटा',
      demoMode: 'डेमो मोड',
    },
    dashboard: {
      title: 'डैशबोर्ड', subtitle: 'आपका खेत एक नजर में',
      farmHealth: 'खेत स्वास्थ्य', cropHealth: 'फसल स्वास्थ्य',
      diseaseRisk: 'रोग जोखिम', waterEfficiency: 'जल दक्षता',
      sustainability: 'स्थिरता', todayRecs: 'आज की सिफारिशें',
      criticalAlerts: 'गंभीर अलर्ट', weatherConditions: 'मौसम',
      sensorStatus: 'सेंसर स्थिति', recentActivities: 'हाल की गतिविधियां',
      aiInsights: 'AI अंतर्दृष्टि',
    },
    disease: {
      title: 'रोग पहचान', upload: 'पत्ती की छवि अपलोड करें',
      drag: 'खींचें और छोड़ें या क्लिक करें', analyze: 'विश्लेषण करें',
      result: 'रोग मिला', confidence: 'विश्वास', risk: 'जोखिम',
      recommendations: 'अनुशंसित कार्य', history: 'भविष्यवाणी इतिहास',
      noModel: 'मॉडल प्रशिक्षित नहीं है',
      lowConfidence: 'कम विश्वास — स्पष्ट छवि अपलोड करें',
      gradcam: 'AI ध्यान मानचित्र',
    },
    alerts: {
      title: 'अलर्ट', markRead: 'पढ़ा हुआ चिह्नित', markAllRead: 'सभी पढ़ें',
      noAlerts: 'कोई अलर्ट नहीं', critical: 'गंभीर', high: 'उच्च',
      medium: 'मध्यम', low: 'निम्न',
    },
  },
  gu: {
    nav: {
      dashboard: 'ડેશબોર્ડ', farms: 'મારા ખેત', plots: 'પ્લોટ', crops: 'પાક',
      activities: 'પ્રવૃત્તિઓ', workers: 'કામદારો', expenses: 'ખર્ચ',
      inventory: 'ભંડાર', disease: 'રોગ શોધ', recommendation: 'પાક ભલામણ',
      irrigation: 'સિંચાઈ', weather: 'હવામાન', advisor: 'AI સલાહકાર',
      assistant: 'AI સહાયક', alerts: 'ચેતવણી', analytics: 'વિશ્લેષण',
      reports: 'અહેવાલ', sensors: 'સેન્સર', settings: 'સેટિંગ',
    },
    common: {
      save: 'સાચવો', cancel: 'રદ કરો', delete: 'કાઢો', edit: 'સંપાદन', add: 'ઉમેરો',
      loading: 'લોડ થઈ રહ્યું છે...', submit: 'સબમિટ', close: 'બંધ', back: 'પાછા',
      confirm: 'પુષ્ટિ', yes: 'હા', no: 'ના', search: 'શોધ',
      filter: 'ફિલ્ટર', export: 'નિકાસ', refresh: 'રિફ્રેશ', view: 'જુઓ',
      create: 'બનાવો', update: 'અપડેट', remove: 'દૂર કરો',
      modelNotTrained: 'મોડેલ પ્રશિક્ષિત નથી',
      simulatedData: 'સિમ્યુલેટેડ ડેટા',
      demoMode: 'ડેમો મોડ',
    },
    dashboard: {
      title: 'ડેશબોર્ડ', subtitle: 'તમારો ખેત એક નજરમાં',
      farmHealth: 'ખેત આરોગ્ય', cropHealth: 'પાક આરોગ્ય',
      diseaseRisk: 'રોગ જોખ', waterEfficiency: 'જળ કાર્યક્ષમتا',
      sustainability: 'ટકાઉ', todayRecs: 'આજની ભલામণો',
      criticalAlerts: 'ગંભીर ચેтவणी', weatherConditions: 'હवامান',
      sensorStatus: 'સેн्सर સ્থิতি', recentActivities: 'તазेтрі પ્रवृт्तिઓ',
      aiInsights: 'AI अंतर्दृष्टि',
    },
    disease: {
      title: 'રోগ шод', upload: 'पаन की छवि अपलोड करें',
      drag: 'ড्रॅग एंड ड्रॉप या क्लिक करें', analyze: 'विश्लेषण',
      result: 'रोग मळ्या', confidence: 'विश्वास', risk: 'जोखिम',
      recommendations: 'अनुशंसित क्रिया', history: 'इतिहास',
      noModel: 'мोडेल прशिक्षित नहीं',
      lowConfidence: 'ओछि खात्री — स्पष्ट छवि अपलोड करें',
      gradcam: 'AI лक्ष मानचित्र',
    },
    alerts: {
      title: 'ચेтवणी', markRead: 'वाचलेले चिन्हांकित', markAllRead: 'सभी पढ़ें',
      noAlerts: 'कोई अलर्ट नहीं', critical: 'गंभीर', high: 'ऊच',
      medium: 'मध्यम', low: 'कमी',
    },
  },
}

const LanguageContext = createContext(null)

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('agriflow_lang') || 'en')

  const setLanguage = (l) => {
    setLang(l)
    localStorage.setItem('agriflow_lang', l)
  }

  const t = (section, key) => {
    return TRANSLATIONS[lang]?.[section]?.[key]
      || TRANSLATIONS['en']?.[section]?.[key]
      || key
  }

  return (
    <LanguageContext.Provider value={{ lang, setLanguage, t, translations: TRANSLATIONS[lang] }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider')
  return ctx
}
