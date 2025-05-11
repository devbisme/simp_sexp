import pytest
import re
from simp_sexp import Sexp, prettify_sexp


# Tests for Sexp parsing
def test_parse_simple():
    s = Sexp('(hello world)')
    assert s == ['hello', 'world']

def test_parse_nested():
    s = Sexp('(hello (world))')
    assert s == ['hello', ['world']]
    assert isinstance(s[1], Sexp)

def test_parse_quotes():
    s = Sexp('(hello "world with spaces" \'single quoted\')')
    assert s == ['hello', 'world with spaces', 'single quoted']

def test_parse_numbers():
    s = Sexp('(values 42 3.14)')
    assert s == ['values', 42, 3.14]
    assert isinstance(s[1], int)
    assert isinstance(s[2], float)

def test_parse_complex():
    s = Sexp('(module TEST (layer F.Cu) (tedit 0x5F5B7C83) (attr through_hole))', quote_nums=False)
    assert s == ['module', 'TEST', ['layer', 'F.Cu'], ['tedit', 0x5F5B7C83], ['attr', 'through_hole']]
    assert isinstance(s[2], Sexp)
    assert isinstance(s[3], Sexp)
    assert isinstance(s[4], Sexp)

def test_escaped_quotes():
    s = Sexp('(text "Quote: \\" and another: \\"")')
    assert s == ['text', 'Quote: " and another: "']


# Tests for to_str method
def test_to_str():
    s = Sexp(['hello', 'world'])
    assert s.to_str(break_inc=0) == '(hello "world")'
    
    s = Sexp(['hello', ['world']])
    assert s.to_str(break_inc=0) == '(hello (world))'

def test_to_str_quoting():
    # Test numeric quoting
    s = Sexp(['values', 42, 3.14])
    assert s.to_str(quote_nums=True, break_inc=0) == '(values "42" "3.14")'
    assert s.to_str(quote_nums=False, break_inc=0) == '(values 42 3.14)'
    
    # Test string quoting
    s = Sexp(['items', 'a', 'b'])
    assert s.to_str(quote_strs=True, break_inc=0) == '(items "a" "b")'
    assert s.to_str(quote_strs=False, break_inc=0) == '(items a b)'

    # Test embedded string quoting
    s = Sexp(['text', 'Quote: " and another: "'])
    assert s.to_str(quote_strs=True, break_inc=0) == '(text "Quote: \\" and another: \\"")'
    assert s.to_str(quote_strs=False, break_inc=0) == '(text Quote: " and another: ")'

def test_prettify():
    s = Sexp(['module', 'TEST', ['layer', 'F.Cu'], ['attr', 'smd'], ['pad', 1, 'smd', ['rect', 100, 100]]])
    pretty = s.to_str(indent=2)  # Changed from spaces_per_level to indent
    assert '\n' in pretty  # Should contain newlines
    
    compact = s.to_str(break_inc=0)
    assert '\n' not in compact  # Should not contain newlines
    
    # With break_inc=2
    with_breaks = s.to_str(break_inc=2)
    # Should have some newlines but fewer than the default
    assert '\n' in with_breaks
    assert with_breaks.count('\n') < pretty.count('\n')

def test_prettify_spaces():
    sexp = "(hello (world))"
    pretty = prettify_sexp(sexp, indent=4)  # Changed from spaces_per_level to indent
    assert "    " in pretty  # Should use 4 spaces for indentation


# Tests for searching
def test_search_value():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Search by value (first element in a list)
    results = s.search('pad')  # Now uses key_path search by default for strings
    assert len(results) == 2
    assert results[0][1][0] == 'pad'
    assert results[1][1][0] == 'pad'
    
    # Search by other value
    results = s.search('layer')  # Now uses key_path search
    assert len(results) == 1
    assert results[0][1] == ['layer', 'F.Cu']

def test_search_keypath():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Relative path
    results = s.search('pad')  # Default behavior for strings
    assert len(results) == 2
    
    # Absolute path
    results = s.search('/module/pad')  # Absolute path notation
    assert len(results) == 2
    
    # Path that doesn't exist
    results = s.search('/other/pad')
    assert len(results) == 0

def test_search_function():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Search for lists with more than 3 elements
    results = s.search(lambda x: len(x) > 3)  # No search_type needed, determined by callable
    assert len(results) == 3  # Both pad elements have 4 elements and the module has 5.
    
    # Search for specific first element and value
    results = s.search(lambda x: x[0] == 'pad' and x[1] == 1)
    assert len(results) == 1
    assert results[0][1] == ['pad', 1, 'smd', 'rect']

def test_search_regex():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Search using regex
    results = s.search(re.compile(r'^pa'))  # No search_type needed, determined by re.Pattern
    assert len(results) == 2  # Should match "pad" elements
    
    # Search using regex as string (now needs to be compiled as re.Pattern)
    results = s.search(re.compile(r'^la'))
    assert len(results) == 1  # Should match "layer" element

def test_search_contains():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Search for specific value anywhere in the list
    results = s.search('smd', contains=True)  # Now uses contains parameter
    assert len(results) == 2  # Both pad elements contain "smd"
    
    # Search for numeric value
    results = s.search(1, contains=True)
    assert len(results) == 1

def test_search_path():
    s = Sexp('(module TEST (layer F.Cu) (pad 1 smd rect) (pad 2 smd rect))')
    
    # Get the exact path indices from first search
    first_pad_path = s.search('pad')[0][0]
    
    # Use that exact path to find the same element
    results = s.search(first_pad_path)  # No search_type needed, determined by list type
    assert len(results) == 1
    assert results[0][1][0] == 'pad'

def test_search_ignore_case():
    s = Sexp('(Module TEST (Layer F.Cu) (PAD 1 smd rect))')
    
    # Case-sensitive search (default)
    results = s.search('module')
    assert len(results) == 0  # Won't match 'Module'
    
    # Case-insensitive search
    results = s.search('module', ignore_case=True)
    assert len(results) == 1
    assert results[0][1][0] == 'Module'
    
    # Case-insensitive search with contains
    results = s.search('test', contains=True, ignore_case=True)
    assert len(results) == 1

@pytest.fixture
def complex_kicad_pcb():
    """
    Fixture providing a complex KiCad PCB S-expression structure for testing.
    """
    kicad_pcb_sexp = """
    (kicad_pcb (version 20171130) (host pcbnew 5.1.6)
      (general
        (thickness 1.6)
        (drawings 5)
        (tracks 14)
        (zones 0)
        (modules 2)
        (nets 3)
      )
      (layers
        (0 F.Cu signal)
        (31 B.Cu signal)
        (34 B.Paste user)
        (36 B.SilkS user)
      )
      (footprint "Capacitor_SMD:C_0805_2012Metric" (layer "F.Cu")
        (tedit 5F68FEEE)
        (descr "Capacitor SMD 0805 (2012 Metric)")
        (tags "capacitor")
        (property "Reference" "C1" (id 0) (at 0 1.5 0))
        (model "${KICAD6_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0805_2012Metric.wrl"
          (offset (xyz 0 0 0))
          (scale (xyz 1 1 1))
          (rotate (xyz 0 0 0))
        )
        (pad 1 smd roundrect (at -0.95 0) (size 1.2 1.4) (layers F.Cu F.Paste F.Mask))
        (pad 2 smd roundrect (at 0.95 0) (size 1.2 1.4) (layers F.Cu F.Paste F.Mask))
      )
      (footprint "Resistor_SMD:R_0805_2012Metric" (layer "F.Cu")
        (tedit 5F68FEEE)
        (descr "Resistor SMD 0805 (2012 Metric)")
        (tags "resistor")
        (property "Reference" "R1" (id 0) (at 0 1.5 0))
        (model "${KICAD6_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0805_2012Metric.wrl"
          (offset (xyz 0 0 0))
          (scale (xyz 1 1 1))
          (rotate (xyz 0 0 0))
        )
        (pad 1 smd roundrect (at -0.95 0) (size 1.2 1.4) (layers F.Cu F.Paste F.Mask))
        (pad 2 smd roundrect (at 0.95 0) (size 1.2 1.4) (layers F.Cu F.Paste F.Mask))
        (pad 3 smd roundrect (at 0 0) (size 0.8 0.8) (layers F.Cu F.Paste F.Mask))
      )
      (net 0 "")
      (net 1 "GND")
      (net 2 "VCC")
    )
    """
    return Sexp(kicad_pcb_sexp)


# Tests for complex search functionality
def test_absolute_path_search(complex_kicad_pcb):
    """Test searching by absolute path."""
    # Find all footprints
    results = complex_kicad_pcb.search('/kicad_pcb/footprint')  # Absolute path
    assert len(results) == 2
    assert results[0][1][0] == 'footprint'
    assert 'Capacitor_SMD:C_0805_2012Metric' in results[0][1][1]
    assert 'Resistor_SMD:R_0805_2012Metric' in results[1][1][1]

    # Find all properties using absolute path
    results = complex_kicad_pcb.search('/kicad_pcb/footprint/property')
    assert len(results) == 2
    assert all(match[0] == 'property' for _, match in results)
    assert any('C1' in match for _, match in results)
    assert any('R1' in match for _, match in results)


def test_relative_path_search(complex_kicad_pcb):
    """Test searching by relative path."""
    # Find all pads regardless of location
    results = complex_kicad_pcb.search('pad')  # Relative path
    assert len(results) == 5  # 2 in capacitor + 3 in resistor
    
    # Find all layer entries regardless of location
    results = complex_kicad_pcb.search('layer')
    assert len(results) == 2  # 2 in footprints


def test_multi_level_path(complex_kicad_pcb):
    """Test searching with multi-level paths."""
    # Find all model elements contained in footprints
    results = complex_kicad_pcb.search('footprint/model')
    assert len(results) == 2
    assert all('3dshapes' in str(match[1]) for _, match in results)
    
    # Find all rotate elements within models
    results = complex_kicad_pcb.search('model/rotate')
    assert len(results) == 2
    assert all(match == ['rotate', ['xyz', 0, 0, 0]] for _, match in results)


def test_function_search(complex_kicad_pcb):
    """Test searching with a custom function."""
    # Find all SMD pads with size 1.2 x 1.4
    def find_specific_pads(sublist):
        if not isinstance(sublist, list) or len(sublist) < 5:
            return False
        return (sublist[0] == 'pad' and 
                'smd' in sublist and 
                'roundrect' in sublist and
                any(isinstance(item, list) and item[0] == 'size' and 
                    item[1] == 1.2 and item[2] == 1.4 for item in sublist))
    
    results = complex_kicad_pcb.search(find_specific_pads)  # Function pattern automatically detected
    assert len(results) == 4  # 2 pads in capacitor + 2 pads in resistor with size 1.2x1.4


def test_regex_search(complex_kicad_pcb):
    """Test searching with regex patterns."""
    import re
    
    # Find all elements starting with 'net'
    results = complex_kicad_pcb.search(re.compile(r'^net$'))  # Regex pattern automatically detected
    assert len(results) == 3  # net 0, net 1, net 2
    
    # Find elements containing layer or layers
    results = complex_kicad_pcb.search(re.compile(r'layer'))
    assert len(results) == 8


def test_combined_searches(complex_kicad_pcb):
    """Test combining multiple search results."""
    # Find capacitor footprint
    capacitor = complex_kicad_pcb.search('Capacitor_SMD:C_0805_2012Metric', contains=True)
    assert len(capacitor) == 1
    capacitor_path = capacitor[0][0]
    
    # Find pads in the capacitor footprint
    capacitor_pads = []
    for i, item in enumerate(complex_kicad_pcb[capacitor_path[0]]):
        if isinstance(item, list) and item and item[0] == 'pad':
            capacitor_pads.append(item)
    
    assert len(capacitor_pads) == 2
    assert all(pad[0] == 'pad' for pad in capacitor_pads)
    
    # Alternative approach using search with path constraint
    resistor = complex_kicad_pcb.search('Resistor_SMD:R_0805_2012Metric', contains=True)
    assert len(resistor) == 1
    resistor_path = resistor[0][0]
    
    # Find pads only within this specific footprint
    resistor_sexp = complex_kicad_pcb[resistor_path[0]]
    resistor_pads = resistor_sexp.search('pad')
    assert len(resistor_pads) == 3  # Resistor has 3 pads


def test_counting_and_verification(complex_kicad_pcb):
    """Test statistical analysis of the S-expression."""
    # Count total number of pads in the PCB
    all_pads = complex_kicad_pcb.search('pad')
    assert len(all_pads) == 5  # 2 in capacitor + 3 in resistor
    
    # Count number of layers
    layers = complex_kicad_pcb.search('/kicad_pcb/layers/0')  # First-level elements in layers
    assert len(layers) == 1
    
    # Verify the layer structure
    layers_section = complex_kicad_pcb.search('layers')[0][1]
    assert isinstance(layers_section, Sexp)
    assert len(layers_section) == 5  # 'layers' + 4 layer definitions
    
    # Verify nets
    # Replaced 'value' search_type with direct path search
    nets = complex_kicad_pcb.search('net')
    assert len(nets) == 3
    net_names = [match[2] for _, match in nets if len(match) > 2]
    assert set(net_names) == set(['', 'GND', 'VCC'])


def test_deep_nested_structure(complex_kicad_pcb):
    """Test searching in deeply nested structures."""
    # Find 3D model paths (deeply nested)
    model_paths = []
    for _, match in complex_kicad_pcb.search('model'):
        if len(match) > 1:
            model_paths.append(match[1])
    
    assert len(model_paths) == 2
    assert all('KICAD6_3DMODEL_DIR' in path for path in model_paths)
    assert any('Capacitor_SMD.3dshapes' in path for path in model_paths)
    assert any('Resistor_SMD.3dshapes' in path for path in model_paths)
    
    # Find all rotation specifications (xyz 0 0 0)
    rotations = complex_kicad_pcb.search('xyz', contains=True)  # Now using contains=True
    assert len(rotations) == 6  # 3 for each model (offset, scale, rotate)
