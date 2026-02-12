import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';

// English translations
import enAuth from './locales/en/auth.json';
import enCommon from './locales/en/common.json';
import enCreateEvent from './locales/en/createEvent.json';
import enEvents from './locales/en/events.json';

// Indonesian translations
import idAuth from './locales/id/auth.json';
import idCommon from './locales/id/common.json';
import idCreateEvent from './locales/id/createEvent.json';
import idEvents from './locales/id/events.json';

const resources = {
  en: {
    common: enCommon,
    events: enEvents,
    auth: enAuth,
    createEvent: enCreateEvent,
  },
  id: {
    common: idCommon,
    events: idEvents,
    auth: idAuth,
    createEvent: idCreateEvent,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "id",
    defaultNS: "common",
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "language",
    },
    interpolation: {
      escapeValue: false,
    },
  });


export default i18n;