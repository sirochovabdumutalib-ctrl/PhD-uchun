-- OAK talablari bo'yicha pandoc -> LaTeX filtri
local roman = {I=1, II=2, III=3, IV=4, V=5}
local chap, eq = 0, 0
local function raw(s) return pandoc.RawBlock('latex', s) end
local function tex(inl) return pandoc.write(pandoc.Pandoc({pandoc.Plain(inl)}), 'latex'):gsub('\n$','') end

function Header(h)
  local txt = pandoc.utils.stringify(h.content)
  if h.level == 1 then
    local r = txt:match('^([IVX]+) BOB')
    if r then chap = roman[r]; eq = 0 end
    return raw('\\oakbob{' .. tex(h.content) .. '}')
  else
    if txt:match('^%d+%-ilova$') then return raw('\\oakilova{' .. txt .. '}') end
    return raw('\\oakpar{' .. tex(h.content) .. '}')
  end
end

function Div(d)
  local cs = d.attributes['custom-style']
  local inl = d.content[1] and d.content[1].content or {}
  if cs == 'Jadval-raqam' then return raw('\\oakjadvalnum{' .. tex(inl) .. '}') end
  if cs == 'Sarlavha-rasm' then return raw('\\oakrasm{' .. tex(inl) .. '}') end
  if cs == 'Sarlavha-jadval' then return raw('\\oakilovanom{' .. tex(inl) .. '}') end
  return nil
end

function Para(p)
  if #p.content == 1 and p.content[1].t == 'Image' then
    return raw('\\oakimg{' .. p.content[1].src .. '}')
  end
  if #p.content == 1 and p.content[1].t == 'Math' and p.content[1].mathtype == 'DisplayMath' then
    local txt = p.content[1].text
    local body, num = txt:match('^(.-)%s*\\qquad\\qquad%s*%((%d+%.%d+)%)%s*$')
    if not num then return nil end
    return raw('\\begin{equation}\\tag{' .. num .. '}\n' .. body .. '\n\\end{equation}')
  end
end

function Span(s)
  if s.attributes['custom-style'] == 'Toldirish' then
    local out = {}
    for _, x in ipairs(s.content) do
      if x.t == 'Str' then table.insert(out, pandoc.RawInline('latex', '\\toldir{' .. tex({x}) .. '}'))
      else table.insert(out, x) end
    end
    return out
  end
end

function Table(t)
  -- ustun kengliklari: matn uzunligiga qarab
  local n = #t.colspecs; local lw, cl = {}, {}
  for i = 1, n do lw[i] = 2; cl[i] = 2 end
  local function longword(s) local m = 0; for wd in s:gmatch('%S+') do m = math.max(m, utf8.len(wd) or #wd) end; return m end
  local function scan(rows, head)
    for _, r in ipairs(rows) do
      for i, c in ipairs(r.cells) do
        local s = pandoc.utils.stringify(c.contents); local L = utf8.len(s) or #s
        if i <= n then
          lw[i] = math.max(lw[i], longword(s) * (head and 0.98 or 1.0))
          cl[i] = math.max(cl[i], head and math.min(L / 2, 14) or math.min(L, 30))
        end
      end
    end
  end
  scan(t.head.rows, true); for _, b in ipairs(t.bodies) do scan(b.body, false) end
  local avail = 467
  local fs, sep
  for _, f in ipairs({12, 11, 10, 9}) do
    fs = f; sep = (f == 12) and 4 or 2.5
    local need = 0; for i = 1, n do need = need + lw[i] * 0.57 * f + 2 * sep + 0.4 end
    if need <= avail then break end
  end
  local inner = avail - n * (2 * sep + 0.4)
  local base, sb, sc = {}, 0, 0
  for i = 1, n do base[i] = lw[i] * 0.57 * fs; sb = sb + base[i]; sc = sc + cl[i] end
  local extra = math.max(inner - sb, 0)
  local wsum = 0; local W = {}
  for i = 1, n do W[i] = base[i] + extra * cl[i] / sc; wsum = wsum + W[i] end
  for i = 1, n do t.colspecs[i] = {t.colspecs[i][1], W[i] / wsum} end
  for _, r in ipairs(t.head.rows) do
    for _, c in ipairs(r.cells) do
      c.contents = pandoc.walk_block(pandoc.Div(c.contents), {Plain = function(p) return pandoc.Plain({pandoc.Strong(p.content)}) end}).content
    end
  end
  return {pandoc.RawBlock('latex', string.format('{\\fontsize{%s}{%s}\\selectfont\\setlength{\\tabcolsep}{%spt}', fs, fs + 2, sep)), t, pandoc.RawBlock('latex', '}')}
end
