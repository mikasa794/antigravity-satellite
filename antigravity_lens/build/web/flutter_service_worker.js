'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"assets/AssetManifest.bin": "70ce98dbcbc928f402692f58b4d42b9f",
"assets/AssetManifest.bin.json": "260edb559086fa705efdd2b926b262d8",
"assets/AssetManifest.json": "b1fbd3e1dc788f3a765bff8cdf7bea29",
"assets/assets/avatars/antigravity.png": "5a4c1feb2c2453412013de57cc531d62",
"assets/assets/avatars/grandpa_icon.png": "b3aba7bbb09dca6535385f30fb440361",
"assets/assets/avatars/hima.png": "cc2dd91689f2a6adac122da3d63872d3",
"assets/assets/avatars/himawari_icon.png": "9a47a7d3499cb51a6055f7fdb66bf788",
"assets/assets/avatars/hiroshi.png": "7cbda036f594cef5a361610d5f114710",
"assets/assets/avatars/hiroshi_icon.png": "8c5c4e551271f1d12a48d317c20d4281",
"assets/assets/avatars/misae.png": "20123984601920f61fa604a6dea6de0d",
"assets/assets/avatars/misae_icon.png": "87d9ce28ceaf92ca31be5f8aaaeb62bf",
"assets/assets/avatars/shin.png": "bfa92408347b261f6b0d09c31fc59388",
"assets/assets/avatars/shinchan_icon.png": "4b0870b9bb437fe65d3cd0fb81057b34",
"assets/assets/avatars/shiro.png": "2eda8ea5d4e003f8636e2d0ea8f8c5ef",
"assets/assets/avatars/shiro_icon.png": "373e8ab3db09ada884bd0a8001e562a3",
"assets/assets/splash_bg.png": "37392a5d449a07d3ce552fa6abb84200",
"assets/assets/splash_boing.wav": "238b53d54a560d4cb28d2749d740f54d",
"assets/assets/splash_char_final.png": "0a4bb07750e13cf45f72468f3c9554db",
"assets/assets/splash_char_intro.png": "08f1953c8b72249e2c2aed5da9ab9599",
"assets/assets/splash_final.jpg": "c9817dcdec2a3527f8869629e1043030",
"assets/assets/splash_intro.jpg": "cd009296116929ec91432bd0fef20ab7",
"assets/assets/splash_jingle.wav": "923053567923f350cf3b5f080b208575",
"assets/assets/splash_magic.wav": "8db23c4ba2c360897b15c37d557f5ae4",
"assets/assets/splash_new_others.wav": "851e79cd35fd977cf829688f097adb37",
"assets/assets/splash_pop.wav": "fc9a9969921278a3d8da6398f81db9e2",
"assets/assets/splash_source.mp3": "e8f4ca36b36ff772afb73af17f3293ff",
"assets/FontManifest.json": "dc3d03800ccca4601324923c0b1d6d57",
"assets/fonts/MaterialIcons-Regular.otf": "fe599ed850753c998a0c415d44492c8e",
"assets/NOTICES": "38d2217870f678c2e3722382d7cbfeaf",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "e986ebe42ef785b27164c36a9abc7818",
"assets/shaders/ink_sparkle.frag": "4096b5150bac93c41cbc9b45276bd90f",
"canvaskit/canvaskit.js": "eb8797020acdbdf96a12fb0405582c1b",
"canvaskit/canvaskit.wasm": "73584c1a3367e3eaf757647a8f5c5989",
"canvaskit/chromium/canvaskit.js": "0ae8bbcc58155679458a0f7a00f66873",
"canvaskit/chromium/canvaskit.wasm": "143af6ff368f9cd21c863bfa4274c406",
"canvaskit/skwasm.js": "87063acf45c5e1ab9565dcf06b0c18b8",
"canvaskit/skwasm.wasm": "2fc47c0a0c3c7af8542b601634fe9674",
"canvaskit/skwasm.worker.js": "bfb704a6c714a75da9ef320991e88b03",
"favicon.png": "5a4c1feb2c2453412013de57cc531d62",
"flutter.js": "59a12ab9d00ae8f8096fffc417b6e84f",
"icons/Icon-192.png": "5a4c1feb2c2453412013de57cc531d62",
"icons/Icon-512.png": "5a4c1feb2c2453412013de57cc531d62",
"icons/Icon-maskable-192.png": "c457ef57daa1d16f64b27b786ec2ea3c",
"icons/Icon-maskable-512.png": "301a7604d45b3e739efc881eb04896ea",
"index.html": "5133a760fca2b9fbc989a251e377ba6a",
"/": "5133a760fca2b9fbc989a251e377ba6a",
"main.dart.js": "cdd79f5e5631f41b48e5855199b47e16",
"manifest.json": "ba43eeb888f17f50ffbbc45c1e64c4d2",
"version.json": "cf2d29b47bb7ba91440604a5c65373f9"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"assets/AssetManifest.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
