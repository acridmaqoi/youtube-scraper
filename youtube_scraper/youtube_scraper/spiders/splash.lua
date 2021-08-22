function main(splash)
  splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
  assert(splash:go(splash.args.url))

  local function isempty(s)
    return s == nil or s == ''
  end

  local element_xpath = "//*[@id='dismissible']/div/div[1]/a//@href"

  while isempty(splash:evaljs("document.evaluate(\"" .. element_xpath .. "\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue")) do
    splash:wait(0.001)
  end

  return {html=splash:html()}
end
