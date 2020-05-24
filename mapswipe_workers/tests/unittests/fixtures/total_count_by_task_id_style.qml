<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" readOnly="0" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1" styleCategories="AllStyleCategories" simplifyDrawingHints="1" version="3.4.6-Madeira" minScale="1e+8" simplifyDrawingTol="1" simplifyLocal="1" maxScale="0" labelsEnabled="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" enableorderby="0" type="categorizedSymbol" symbollevels="0" attr="CASE&#xa;  WHEN  &quot;total_results_count&quot; = 0 THEN 0&#xa;  WHEN  &quot;total_results_count&quot; = 1 THEN 1&#xa;  WHEN  &quot;total_results_count&quot; = 2 THEN 2&#xa;  WHEN  &quot;total_results_count&quot; = 3 THEN 3&#xa;  WHEN  &quot;total_results_count&quot; = 4 THEN 4&#xa;  ELSE  5&#xa;END">
    <categories>
      <category symbol="0" value="1" render="true" label="1"/>
      <category symbol="1" value="2" render="true" label="2"/>
      <category symbol="2" value="3" render="true" label="3"/>
      <category symbol="3" value="4" render="true" label="4"/>
      <category symbol="4" value="5" render="true" label=">=5"/>
    </categories>
    <symbols>
      <symbol name="0" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="253,231,37,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="1" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="93,201,98,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="2" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="32,144,141,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="3" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="58,82,139,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="4" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="68,1,84,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol name="0" type="fill" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer enabled="1" pass="0" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="225,89,137,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp name="[source]" type="gradient">
      <prop v="253,231,37,255" k="color1"/>
      <prop v="68,1,84,255" k="color2"/>
      <prop v="0" k="discrete"/>
      <prop v="gradient" k="rampType"/>
      <prop v="0.019608;241,229,29,255:0.039216;229,228,25,255:0.058824;216,226,25,255:0.078431;202,225,31,255:0.098039;189,223,38,255:0.117647;176,221,47,255:0.137255;162,218,55,255:0.156863;149,216,64,255:0.176471;137,213,72,255:0.196078;124,210,80,255:0.215686;112,207,87,255:0.235294;101,203,94,255:0.254902;90,200,100,255:0.27451;80,196,106,255:0.294118;70,192,111,255:0.313725;61,188,116,255:0.333333;53,183,121,255:0.352941;46,179,124,255:0.372549;40,174,128,255:0.392157;36,170,131,255:0.411765;33,165,133,255:0.431373;31,161,136,255:0.45098;30,156,137,255:0.470588;31,151,139,255:0.490196;32,146,140,255:0.509804;33,142,141,255:0.529412;35,137,142,255:0.54902;37,132,142,255:0.568627;39,128,142,255:0.588235;41,123,142,255:0.607843;42,118,142,255:0.627451;44,113,142,255:0.647059;46,109,142,255:0.666667;49,104,142,255:0.686275;51,99,141,255:0.705882;53,94,141,255:0.72549;56,89,140,255:0.745098;58,83,139,255:0.764706;61,78,138,255:0.784314;63,72,137,255:0.803922;65,66,135,255:0.823529;67,61,132,255:0.843137;69,55,129,255:0.862745;70,48,126,255:0.882353;71,42,122,255:0.901961;72,36,117,255:0.921569;72,29,111,255:0.941176;72,23,105,255:0.960784;71,16,99,255:0.980392;70,8,92,255" k="stops"/>
    </colorramp>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory penAlpha="255" penWidth="0" rotationOffset="270" backgroundColor="#ffffff" scaleDependency="Area" width="15" maxScaleDenominator="1e+8" barWidth="5" minimumSize="0" height="15" minScaleDenominator="0" enabled="0" sizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" penColor="#000000" scaleBasedVisibility="0" lineSizeScale="3x:0,0,0,0,0,0" backgroundAlpha="255" opacity="1" labelPlacementMethod="XHeight" lineSizeType="MM" sizeType="MM">
      <fontProperties style="" description="Ubuntu,11,-1,5,50,0,0,0,0,0"/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" dist="0" placement="1" priority="0" zIndex="0" obstacle="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="project_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="group_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="task_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="total_results_count">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="0_results_count">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="1_results_count">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="2_results_count">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="3_results_count">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="0_results_share">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="1_results_share">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="2_results_share">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="3_results_share">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="first_timestamp">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="last_timestamp">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="agreement">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="project_id" name="" index="0"/>
    <alias field="group_id" name="" index="1"/>
    <alias field="task_id" name="" index="2"/>
    <alias field="total_results_count" name="" index="3"/>
    <alias field="0_results_count" name="" index="4"/>
    <alias field="1_results_count" name="" index="5"/>
    <alias field="2_results_count" name="" index="6"/>
    <alias field="3_results_count" name="" index="7"/>
    <alias field="0_results_share" name="" index="8"/>
    <alias field="1_results_share" name="" index="9"/>
    <alias field="2_results_share" name="" index="10"/>
    <alias field="3_results_share" name="" index="11"/>
    <alias field="first_timestamp" name="" index="12"/>
    <alias field="last_timestamp" name="" index="13"/>
    <alias field="agreement" name="" index="14"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="project_id" applyOnUpdate="0"/>
    <default expression="" field="group_id" applyOnUpdate="0"/>
    <default expression="" field="task_id" applyOnUpdate="0"/>
    <default expression="" field="total_results_count" applyOnUpdate="0"/>
    <default expression="" field="0_results_count" applyOnUpdate="0"/>
    <default expression="" field="1_results_count" applyOnUpdate="0"/>
    <default expression="" field="2_results_count" applyOnUpdate="0"/>
    <default expression="" field="3_results_count" applyOnUpdate="0"/>
    <default expression="" field="0_results_share" applyOnUpdate="0"/>
    <default expression="" field="1_results_share" applyOnUpdate="0"/>
    <default expression="" field="2_results_share" applyOnUpdate="0"/>
    <default expression="" field="3_results_share" applyOnUpdate="0"/>
    <default expression="" field="first_timestamp" applyOnUpdate="0"/>
    <default expression="" field="last_timestamp" applyOnUpdate="0"/>
    <default expression="" field="agreement" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" field="project_id" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="group_id" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="task_id" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="total_results_count" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="0_results_count" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="1_results_count" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="2_results_count" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="3_results_count" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="0_results_share" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="1_results_share" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="2_results_share" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="3_results_share" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="first_timestamp" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="last_timestamp" exp_strength="0" notnull_strength="0" constraints="0"/>
    <constraint unique_strength="0" field="agreement" exp_strength="0" notnull_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="project_id" exp="" desc=""/>
    <constraint field="group_id" exp="" desc=""/>
    <constraint field="task_id" exp="" desc=""/>
    <constraint field="total_results_count" exp="" desc=""/>
    <constraint field="0_results_count" exp="" desc=""/>
    <constraint field="1_results_count" exp="" desc=""/>
    <constraint field="2_results_count" exp="" desc=""/>
    <constraint field="3_results_count" exp="" desc=""/>
    <constraint field="0_results_share" exp="" desc=""/>
    <constraint field="1_results_share" exp="" desc=""/>
    <constraint field="2_results_share" exp="" desc=""/>
    <constraint field="3_results_share" exp="" desc=""/>
    <constraint field="first_timestamp" exp="" desc=""/>
    <constraint field="last_timestamp" exp="" desc=""/>
    <constraint field="agreement" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column hidden="0" name="project_id" width="-1" type="field"/>
      <column hidden="0" name="group_id" width="-1" type="field"/>
      <column hidden="0" name="task_id" width="-1" type="field"/>
      <column hidden="0" name="total_results_count" width="-1" type="field"/>
      <column hidden="0" name="0_results_count" width="-1" type="field"/>
      <column hidden="0" name="1_results_count" width="-1" type="field"/>
      <column hidden="0" name="2_results_count" width="-1" type="field"/>
      <column hidden="0" name="3_results_count" width="-1" type="field"/>
      <column hidden="0" name="0_results_share" width="-1" type="field"/>
      <column hidden="0" name="1_results_share" width="-1" type="field"/>
      <column hidden="0" name="2_results_share" width="-1" type="field"/>
      <column hidden="0" name="3_results_share" width="-1" type="field"/>
      <column hidden="0" name="first_timestamp" width="-1" type="field"/>
      <column hidden="0" name="last_timestamp" width="-1" type="field"/>
      <column hidden="0" name="agreement" width="-1" type="field"/>
      <column hidden="1" width="-1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="0_results_count"/>
    <field editable="1" name="0_results_share"/>
    <field editable="1" name="1_results_count"/>
    <field editable="1" name="1_results_share"/>
    <field editable="1" name="2_results_count"/>
    <field editable="1" name="2_results_share"/>
    <field editable="1" name="3_results_count"/>
    <field editable="1" name="3_results_share"/>
    <field editable="1" name="agreement"/>
    <field editable="1" name="first_timestamp"/>
    <field editable="1" name="group_id"/>
    <field editable="1" name="last_timestamp"/>
    <field editable="1" name="project_id"/>
    <field editable="1" name="task_id"/>
    <field editable="1" name="total_results_count"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="0_results_count"/>
    <field labelOnTop="0" name="0_results_share"/>
    <field labelOnTop="0" name="1_results_count"/>
    <field labelOnTop="0" name="1_results_share"/>
    <field labelOnTop="0" name="2_results_count"/>
    <field labelOnTop="0" name="2_results_share"/>
    <field labelOnTop="0" name="3_results_count"/>
    <field labelOnTop="0" name="3_results_share"/>
    <field labelOnTop="0" name="agreement"/>
    <field labelOnTop="0" name="first_timestamp"/>
    <field labelOnTop="0" name="group_id"/>
    <field labelOnTop="0" name="last_timestamp"/>
    <field labelOnTop="0" name="project_id"/>
    <field labelOnTop="0" name="task_id"/>
    <field labelOnTop="0" name="total_results_count"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>project_id</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
